"""Sign-In With Ethereum (EIP-4361) implementation.

The :class:`SiweAuthenticator` mints a nonce, builds a SIWE message,
and - once the user signs it - verifies the signature and issues a
short-lived session token. Sessions are stored in memory by default;
swap in a Redis backend via :py:meth:`SiweAuthenticator.with_session_store`.

This is a self-contained implementation that does not require
``siwe`` (the npm package) - it follows the EIP-4361 grammar
directly. The message format is:

    <domain> wants you to sign in with your Ethereum account:
    <address>

    <statement>

    URI: <uri>
    Version: 1
    Chain ID: <chain id>
    Nonce: <nonce>
    Issued At: <iso-8601>
    Expiration Time: <iso-8601>
    Not Before: <iso-8601>
    Request ID: <uuid>
    Resources:
    - <uri>
    - <uri>
"""

from __future__ import annotations

import logging
import secrets
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Protocol

from .signature import SignatureVerifier, VerificationResult

logger = logging.getLogger("laniakea.web3.siwe")


def _iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%S%.fZ"
    )


@dataclass
class SiweMessage:
    """Parsed EIP-4361 SIWE message.

    The :py:meth:`render` method serializes back into the canonical
    text the wallet signs. Parsing is intentionally permissive - the
    goal is to validate, not to be a complete EIP-4361 reference.
    """

    domain: str
    address: str
    uri: str
    chain_id: int
    nonce: str
    issued_at: float
    expiration_time: Optional[float] = None
    not_before: Optional[float] = None
    request_id: Optional[str] = None
    statement: Optional[str] = None
    resources: List[str] = field(default_factory=list)
    version: str = "1"

    def render(self) -> str:
        """Serialize to the exact EIP-4361 text format."""
        lines: List[str] = []
        lines.append(f"{self.domain} wants you to sign in with your Ethereum account:")
        lines.append(self.address)
        lines.append("")
        if self.statement:
            lines.append(self.statement)
            lines.append("")
        lines.append(f"URI: {self.uri}")
        lines.append(f"Version: {self.version}")
        lines.append(f"Chain ID: {self.chain_id}")
        lines.append(f"Nonce: {self.nonce}")
        lines.append(f"Issued At: {_iso(self.issued_at)}")
        if self.expiration_time is not None:
            lines.append(f"Expiration Time: {_iso(self.expiration_time)}")
        if self.not_before is not None:
            lines.append(f"Not Before: {_iso(self.not_before)}")
        if self.request_id is not None:
            lines.append(f"Request ID: {self.request_id}")
        if self.resources:
            lines.append("Resources:")
            for r in self.resources:
                lines.append(f"- {r}")
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "domain": self.domain,
            "address": self.address,
            "uri": self.uri,
            "chain_id": self.chain_id,
            "nonce": self.nonce,
            "issued_at": _iso(self.issued_at),
            "expiration_time": (
                _iso(self.expiration_time) if self.expiration_time else None
            ),
            "not_before": (_iso(self.not_before) if self.not_before else None),
            "request_id": self.request_id,
            "statement": self.statement,
            "resources": list(self.resources),
            "version": self.version,
        }

    @classmethod
    def parse(cls, raw: str) -> "SiweMessage":
        """Parse a SIWE message back into a struct.

        Only the fields Laniakea actually uses are strictly enforced;
        unknown headers are tolerated so the verifier stays forward-
        compatible with future EIP-4361 extensions.
        """
        lines = raw.split("\n")
        if len(lines) < 6:
            raise ValueError("SIWE message too short")
        # Header line: "<domain> wants you to sign in with your Ethereum account:"
        header = lines[0]
        if " wants you to sign in with your Ethereum account:" not in header:
            raise ValueError("invalid SIWE header line")
        domain = header.split(" wants you to sign in", 1)[0].strip()
        address = lines[1].strip()
        # Find first "URI:" line - the lines before it are the body.
        uri_idx = None
        for i, ln in enumerate(lines):
            if ln.startswith("URI: "):
                uri_idx = i
                break
        if uri_idx is None:
            raise ValueError("SIWE message missing URI")
        body = lines[2:uri_idx]
        statement = None
        if body and body[0].strip() != "":
            statement = "\n".join(body).strip() or None
        fields: Dict[str, str] = {}
        i = uri_idx
        resources: List[str] = []
        in_resources = False
        while i < len(lines):
            ln = lines[i]
            if in_resources:
                if ln.startswith("- "):
                    resources.append(ln[2:].strip())
                i += 1
                continue
            if ":" in ln:
                k, v = ln.split(":", 1)
                if k.strip() == "Resources":
                    in_resources = True
                else:
                    fields[k.strip()] = v.strip()
            i += 1
        try:
            chain_id = int(fields.get("Chain ID", ""))
        except ValueError as exc:
            raise ValueError("SIWE Chain ID must be int") from exc
        return cls(
            domain=domain,
            address=address,
            uri=fields.get("URI", ""),
            chain_id=chain_id,
            nonce=fields.get("Nonce", ""),
            issued_at=_parse_iso(fields.get("Issued At", "")),
            expiration_time=(
                _parse_iso(fields["Expiration Time"])
                if "Expiration Time" in fields
                else None
            ),
            not_before=(
                _parse_iso(fields["Not Before"])
                if "Not Before" in fields
                else None
            ),
            request_id=fields.get("Request ID"),
            statement=statement,
            resources=resources,
            version=fields.get("Version", "1"),
        )


def _parse_iso(s: str) -> float:
    s = s.strip()
    # Python's fromisoformat handles "...Z" only from 3.11+.
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    dt = datetime.fromisoformat(s)
    return dt.timestamp()


# ----------------------------------------------------------------------------
# Nonce + Session stores
# ----------------------------------------------------------------------------


class NonceStore(Protocol):
    """Storage backend for issued SIWE nonces.

    Implementations must support the four methods below. The default
    in-memory store is fine for single-process deployments; for
    multi-instance production swap in Redis or similar.
    """

    def reserve(self, nonce: str, ttl_seconds: int) -> None: ...
    def consume(self, nonce: str) -> bool: ...
    def purge_expired(self) -> int: ...


class InMemoryNonceStore:
    """Thread-safe in-process nonce store."""

    def __init__(self) -> None:
        self._data: Dict[str, float] = {}
        self._lock = threading.Lock()

    def reserve(self, nonce: str, ttl_seconds: int) -> None:
        with self._lock:
            self._data[nonce] = time.time() + ttl_seconds

    def consume(self, nonce: str) -> bool:
        with self._lock:
            expires = self._data.pop(nonce, None)
            if expires is None:
                return False
            if expires < time.time():
                return False
            return True

    def purge_expired(self) -> int:
        now = time.time()
        with self._lock:
            expired = [k for k, v in self._data.items() if v < now]
            for k in expired:
                del self._data[k]
            return len(expired)


class SessionStore(Protocol):
    def put(self, session_id: str, payload: Dict[str, Any], ttl_seconds: int) -> None: ...
    def get(self, session_id: str) -> Optional[Dict[str, Any]]: ...
    def revoke(self, session_id: str) -> None: ...


class InMemorySessionStore:
    """Thread-safe in-process session store."""

    def __init__(self) -> None:
        self._data: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def put(self, session_id: str, payload: Dict[str, Any], ttl_seconds: int) -> None:
        with self._lock:
            self._data[session_id] = {
                **payload,
                "expires_at": time.time() + ttl_seconds,
            }

    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            entry = self._data.get(session_id)
            if entry is None:
                return None
            if entry["expires_at"] < time.time():
                self._data.pop(session_id, None)
                return None
            return dict(entry)

    def revoke(self, session_id: str) -> None:
        with self._lock:
            self._data.pop(session_id, None)


# ----------------------------------------------------------------------------
# Authenticator
# ----------------------------------------------------------------------------


@dataclass
class SiweAuthenticator:
    """The end-to-end SIWE flow.

    Typical usage::

        auth = SiweAuthenticator(domain="laniakea.example")
        nonce = auth.issue_nonce()
        msg = auth.build_message(address="0xabc...", chain_id=1, nonce=nonce)
        text = msg.render()
        # ... user signs text in their wallet ...
        result = auth.verify_and_issue(
            message=text,
            signature=signature_hex,
            expected_address="0xabc...",
            chain_id=1,
        )
        if result.is_valid:
            session_id = result.session_id

    All time-based fields are absolute UTC timestamps, which makes the
    verifier trivially testable with mocked clocks.
    """

    domain: str
    statement: str = "Sign in to Laniakea Protocol to link this wallet to your SCDA identity."
    uri: str = "https://laniakea.example/login"
    nonce_ttl_seconds: int = 600
    session_ttl_seconds: int = 3600
    nonce_store: NonceStore = field(default_factory=InMemoryNonceStore)
    session_store: SessionStore = field(default_factory=InMemorySessionStore)
    verifier: Optional[SignatureVerifier] = None
    clock: Any = None  # callable returning float seconds; default time.time

    def __post_init__(self) -> None:
        if self.verifier is None:
            self.verifier = SignatureVerifier()
        if self.clock is None:
            self.clock = time.time

    # -- nonce + message construction ------------------------------------
    def issue_nonce(self) -> str:
        """Mint a 17-char alphanumeric nonce and reserve it for `nonce_ttl_seconds`."""
        nonce = secrets.token_urlsafe(12)[:17]
        self.nonce_store.reserve(nonce, self.nonce_ttl_seconds)
        return nonce

    def build_message(
        self,
        address: str,
        chain_id: int,
        nonce: str,
        resources: Optional[List[str]] = None,
    ) -> SiweMessage:
        """Build a SIWE message bound to the supplied address + chain."""
        now = self.clock()
        return SiweMessage(
            domain=self.domain,
            address=address,
            uri=self.uri,
            chain_id=chain_id,
            nonce=nonce,
            issued_at=now,
            expiration_time=now + self.nonce_ttl_seconds,
            not_before=now,
            request_id=str(uuid.uuid4()),
            statement=self.statement,
            resources=list(resources or []),
        )

    # -- verify + session ------------------------------------------------
    def verify_and_issue(
        self,
        message: str,
        signature: str,
        expected_address: str,
        chain_id: int,
    ) -> Dict[str, Any]:
        """Verify a signed SIWE message and issue a session token.

        Returns a dict suitable for JSON: ``{"is_valid": bool, ...,
        "session_id": str|None}``. The caller decides what to do on
        failure; we never raise on bad signatures.
        """
        try:
            parsed = SiweMessage.parse(message)
        except ValueError as exc:
            return {"is_valid": False, "error": f"parse_error: {exc}"}
        if parsed.domain.lower() != self.domain.lower():
            return {"is_valid": False, "error": "domain_mismatch"}
        if parsed.address.lower() != expected_address.lower():
            return {"is_valid": False, "error": "address_mismatch"}
        if parsed.chain_id != chain_id:
            return {"is_valid": False, "error": "chain_id_mismatch"}
        now = self.clock()
        if parsed.expiration_time and parsed.expiration_time < now:
            return {"is_valid": False, "error": "message_expired"}
        if parsed.not_before and parsed.not_before > now:
            return {"is_valid": False, "error": "message_not_yet_valid"}
        if not self.nonce_store.consume(parsed.nonce):
            return {"is_valid": False, "error": "nonce_invalid_or_used"}

        verification: VerificationResult = self.verifier.verify(
            message=message,
            signature=signature,
            wallet=expected_address,
            chain_id=chain_id,
        )
        if not verification.is_valid:
            return {
                "is_valid": False,
                "error": verification.error or "signature_invalid",
                "verification": verification.to_dict(),
            }

        session_id = secrets.token_urlsafe(32)
        self.session_store.put(
            session_id,
            {
                "address": expected_address,
                "chain_id": chain_id,
                "issued_at": now,
                "request_id": parsed.request_id,
            },
            self.session_ttl_seconds,
        )
        return {
            "is_valid": True,
            "session_id": session_id,
            "expires_in": self.session_ttl_seconds,
            "verification": verification.to_dict(),
        }

    def revoke_session(self, session_id: str) -> None:
        self.session_store.revoke(session_id)

    def lookup_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self.session_store.get(session_id)

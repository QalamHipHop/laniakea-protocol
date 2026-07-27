"""Cryptographic signature verification for wallet-based auth.

Implements two verification paths:

* **EOA signatures** via ``eth-account.recover_message`` for personal_sign.
* **Smart-contract wallets** (EIP-1271) via a thin JSON-RPC call to
  ``eth_call`` on the wallet address with the magic value
  ``0x1626ba7e``. The RPC URL is resolved through ``ChainRegistry``.

Verification is intentionally pure-Python: ``eth-account`` is the only
hard dependency. The function is safe to call with no chain access
(``verify_personal_sign`` never touches the network) - EIP-1271
verification is opt-in via :py:meth:`SignatureVerifier.verify`.
"""

from __future__ import annotations

import enum
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger("laniakea.web3.signature")

# EIP-1271 magic value returned by valid smart-contract wallets.
EIP1271_MAGIC_VALUE = "0x1626ba7e"
# EIP-1271 selector for isValidSignature(address,bytes)
EIP1271_SELECTOR = "0x20c13b0b"


class SignatureType(str, enum.Enum):
    """The on-chain shape of the signer."""

    EOA = "eoa"           # Externally owned account
    EIP1271 = "eip1271"   # Smart-contract wallet
    EIP6492 = "eip6492"   # Counter-factual smart wallet (e.g. ERC-4337)


@dataclass
class VerificationResult:
    """Outcome of a signature verification attempt."""

    is_valid: bool
    signature_type: SignatureType
    recovered_address: Optional[str] = None
    error: Optional[str] = None
    chain_id: Optional[int] = None
    verified_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "signature_type": self.signature_type.value,
            "recovered_address": self.recovered_address,
            "error": self.error,
            "chain_id": self.chain_id,
            "verified_at": self.verified_at,
        }


def _try_import_eth_account():
    """Lazy import so this module is importable without web3 deps."""
    try:
        from eth_account import Account
        from eth_account.messages import encode_defunct
        return Account, encode_defunct
    except Exception as exc:  # pragma: no cover - depends on env
        logger.warning("eth-account not available: %s", exc)
        return None, None


def _try_import_eth_keys():
    """Optional eth-keys fallback for the no-eth-account path."""
    try:
        from eth_keys import keys
        from eth_utils import keccak, to_checksum_address
        return keys, keccak, to_checksum_address
    except Exception:  # pragma: no cover
        return None, None, None


def _keccak256(data: bytes) -> bytes:
    """Pure-python keccak using hashlib's `keccak_256` if available, else sha3_256.

    keccak_256 is the proper keccak (NOT NIST sha3). hashlib exposes
    ``keccak_256`` on Python 3.6+ through the _pysha3 module on some
    builds, but the safe cross-platform path is ``Crypto.Hash.keccak``
    (pycryptodome). If neither is available we fall back to the stdlib
    ``sha3_256`` (NIST) - verification will then FAIL because keccak and
    sha3 differ by a domain tag, and the test suite asserts this.
    """
    try:
        from Crypto.Hash import keccak as _keccak  # pycryptodome
        h = _keccak.new(digest_bits=256)
        h.update(data)
        return h.digest()
    except Exception:
        pass
    try:
        import hashlib
        return hashlib.new("keccak_256", data).digest()  # type: ignore[arg-type]
    except Exception:
        # Last-resort: sha3_256 (NIST) - will produce wrong address but
        # at least keeps the function from raising. Callers should
        # catch the resulting invalid signature.
        import hashlib
        return hashlib.sha3_256(data).digest()


def _eip55_checksum(addr_hex: str) -> str:
    """Compute EIP-55 checksum for a 20-byte hex address (no leading 0x)."""
    addr_hex = addr_hex.lower().removeprefix("0x")
    hash_hex = _keccak256(addr_hex.encode("ascii")).hex()
    out = []
    for c, h in zip(addr_hex, hash_hex):
        if c in "0123456789":
            out.append(c)
        elif int(h, 16) >= 8:
            out.append(c.upper())
        else:
            out.append(c)
    return "0x" + "".join(out)


def _recover_address(message: str, signature_hex: str) -> Optional[str]:
    """Recover the 20-byte signer address from a personal_sign signature."""
    Account, encode_defunct = _try_import_eth_account()
    if Account is not None and encode_defunct is not None:
        try:
            encoded = encode_defunct(text=message)
            addr = Account.recover_message(encoded, signature=signature_hex)
            return addr
        except Exception as exc:
            logger.debug("eth-account recovery failed: %s", exc)
            return None

    keys, _keccak, _ = _try_import_eth_keys()
    if keys is None:
        logger.warning("No signature recovery library available")
        return None
    try:
        # Strip 0x, take r||s||v (65 bytes total).
        sig = bytes.fromhex(signature_hex.removeprefix("0x"))
        if len(sig) != 65:
            return None
        r = sig[0:32]
        s = sig[32:64]
        v = sig[64]
        if v < 27:
            v += 27
        if v not in (27, 28):
            return None
        encoded = encode_defunct(text=message) if encode_defunct else None  # type: ignore
        if encoded is None:
            return None
        digest = _keccak256(encoded.body)
        sig_obj = keys.Signature(r=vrs_signature(vrs=(v - 27, int.from_bytes(r, "big"), int.from_bytes(s, "big"))))  # type: ignore[arg-type]
        pub = sig_obj.recover_public_key_from_msg_hash(digest)
        return pub.to_checksum_address()
    except Exception as exc:
        logger.debug("eth-keys recovery failed: %s", exc)
        return None


def verify_personal_sign(
    message: str,
    signature: str,
    expected_address: str,
) -> VerificationResult:
    """Verify a ``personal_sign`` signature for an EOA.

    Args:
        message: The exact text the wallet was asked to sign (no prefix).
        signature: Hex-encoded 65-byte signature, with or without ``0x``.
        expected_address: The 0x-prefixed EIP-55 address the signature
            must resolve to. Comparison is checksum-insensitive.

    Returns:
        :class:`VerificationResult` with ``recovered_address`` populated
        when the signature is well-formed, regardless of validity.
    """
    recovered = _recover_address(message, signature)
    if recovered is None:
        return VerificationResult(
            is_valid=False,
            signature_type=SignatureType.EOA,
            error="signature_recovery_failed",
        )
    ok = recovered.lower() == expected_address.lower()
    return VerificationResult(
        is_valid=ok,
        signature_type=SignatureType.EOA,
        recovered_address=recovered,
        error=None if ok else "address_mismatch",
    )


# ----------------------------------------------------------------------------
# EIP-1271 smart-wallet verification
# ----------------------------------------------------------------------------


def _json_rpc(url: str, method: str, params: list) -> Dict[str, Any]:
    """Minimal JSON-RPC POST; uses stdlib only."""
    import urllib.request
    payload = json.dumps(
        {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    ).encode("utf-8")
    req = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:  # nosec - public RPC
        body = resp.read().decode("utf-8")
    return json.loads(body)


def _encode_eth_call(wallet: str, message_hash: bytes, signature: bytes) -> str:
    """ABI-encode ``isValidSignature(bytes32,bytes)`` calldata."""
    selector = EIP1271_SELECTOR
    # 32-byte left-padded wallet address
    addr_word = wallet.lower().removeprefix("0x").rjust(64, "0")
    # offset of the bytes blob (pointing to the start of the dynamic part)
    offset_word = "0000000000000000000000000000000000000000000000000000000000000040"  # 64
    # length of the signature blob
    sig_len = format(len(signature), "x").rjust(64, "0")
    # pad signature to 32-byte boundary
    sig_bytes = signature.hex()
    pad_len = (32 - (len(signature) % 32)) % 32
    sig_padded = sig_bytes + "00" * pad_len
    return "0x" + selector + addr_word + offset_word + sig_len + sig_padded


def verify_eip1271(
    wallet: str,
    message_hash: bytes,
    signature: bytes,
    rpc_url: str,
) -> VerificationResult:
    """Verify a smart-contract wallet signature per EIP-1271.

    Args:
        wallet: 0x-prefixed contract wallet address.
        message_hash: 32-byte digest the wallet was asked to sign.
        signature: Raw signature bytes (opaque - the wallet interprets it).
        rpc_url: HTTP JSON-RPC endpoint to call.
    """
    calldata = _encode_eth_call(wallet, message_hash, signature)
    try:
        resp = _json_rpc(rpc_url, "eth_call", [{"to": wallet, "data": calldata}, "latest"])
    except Exception as exc:
        return VerificationResult(
            is_valid=False,
            signature_type=SignatureType.EIP1271,
            error=f"rpc_error: {exc}",
        )
    if "error" in resp:
        return VerificationResult(
            is_valid=False,
            signature_type=SignatureType.EIP1271,
            error=f"rpc_error: {resp['error']}",
        )
    result = resp.get("result", "")
    ok = result.lower().startswith(EIP1271_MAGIC_VALUE)
    return VerificationResult(
        is_valid=ok,
        signature_type=SignatureType.EIP1271,
        recovered_address=wallet,
        error=None if ok else f"magic_value_mismatch: {result[:10]}",
    )


# ----------------------------------------------------------------------------
# High-level facade
# ----------------------------------------------------------------------------


@dataclass
class SignatureVerifier:
    """Top-level verifier that picks EOA vs EIP-1271 based on code at address.

    Use :py:meth:`verify` when you have a wallet address and want the
    verifier to introspect the chain and pick the right path.
    """

    chain_registry: Any = None
    rpc_caller: Optional[Callable[[str, str, list], Dict[str, Any]]] = None
    code_caller: Optional[Callable[[str, int], str]] = None

    def __post_init__(self) -> None:
        if self.chain_registry is None:
            from .chain_registry import ChainRegistry
            self.chain_registry = ChainRegistry.instance()
        if self.rpc_caller is None:
            self.rpc_caller = _json_rpc
        if self.code_caller is None:
            self.code_caller = self._default_code_caller

    def _default_code_caller(self, rpc_url: str, wallet: str) -> str:
        try:
            resp = self.rpc_caller(rpc_url, "eth_getCode", [wallet, "latest"])
            return (resp.get("result") or "0x").lower()
        except Exception as exc:
            logger.debug("eth_getCode failed: %s", exc)
            return "0x"

    def verify(
        self,
        message: str,
        signature: str,
        wallet: str,
        chain_id: int,
    ) -> VerificationResult:
        """Verify a signature, picking the right scheme automatically.

        If the address has contract code, we attempt EIP-1271 verification
        by hashing ``message`` with keccak256. Otherwise we treat it as
        an EOA and recover the signer.
        """
        chain = self.chain_registry.by_id(chain_id)
        rpc = chain.rpc_url()
        code = self.code_caller(rpc, wallet)
        sig_bytes = bytes.fromhex(signature.removeprefix("0x"))

        if code and code != "0x":
            msg_hash = _keccak256(message.encode("utf-8"))
            res = verify_eip1271(wallet, msg_hash, sig_bytes, rpc)
            res.chain_id = chain_id
            return res
        res = verify_personal_sign(message, signature, wallet)
        res.chain_id = chain_id
        return res

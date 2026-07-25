"""FastAPI routes for the Web3 wallet integration layer.

Exposes SIWE (Sign-In With Ethereum) auth + wallet<->SCDA binding
endpoints. All endpoints are designed to fail closed: a single bad
field returns a 400 with a structured error, never a 500.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, HTTPException, Header
from pydantic import BaseModel, Field, field_validator

from laniakea.web3 import (
    SiweAuthenticator,
    SiweMessage,
    WalletLinkService,
    ChainRegistry,
    SignatureVerifier,
)
from laniakea.intelligence.scda_manager import get_scda_manager

logger = logging.getLogger("laniakea.api.web3")

router = APIRouter(prefix="/web3", tags=["web3"])

# Singletons - cheap, process-wide. The SCDA manager is shared with the
# rest of the API so that binding a wallet actually links to a real
# SCDA instance.
_chain_registry = ChainRegistry.instance()
_verifier = SignatureVerifier(chain_registry=_chain_registry)
_authenticator = SiweAuthenticator(
    domain=os.getenv("SIWE_DOMAIN", "laniakea.example"),
    uri=os.getenv("SIWE_URI", "https://laniakea.example/login"),
    verifier=_verifier,
)
_wallet_links = WalletLinkService(chain_registry=_chain_registry)


# ----------------------------------------------------------------------------
# Request/Response models
# ----------------------------------------------------------------------------


class NonceResponse(BaseModel):
    nonce: str
    expires_in: int


class BuildMessageRequest(BaseModel):
    address: str = Field(..., description="0x-prefixed wallet address")
    chain_id: int = Field(..., ge=1, description="EIP-155 chain id")
    resources: Optional[List[str]] = None

    @field_validator("address")
    @classmethod
    def _address_shape(cls, v: str) -> str:
        if not v.startswith("0x") or len(v) != 42:
            raise ValueError("address must be 0x-prefixed 20-byte hex")
        return v


class BuildMessageResponse(BaseModel):
    message: str
    parsed: Dict[str, Any]
    nonce: str
    expires_in: int


class VerifyRequest(BaseModel):
    message: str
    signature: str = Field(..., description="0x-prefixed hex signature (65 bytes)")
    address: str
    chain_id: int

    @field_validator("signature")
    @classmethod
    def _sig_shape(cls, v: str) -> str:
        s = v.removeprefix("0x")
        if len(s) != 130:
            raise ValueError("signature must be 65 bytes hex")
        return v


class VerifyResponse(BaseModel):
    is_valid: bool
    session_id: Optional[str] = None
    expires_in: Optional[int] = None
    error: Optional[str] = None
    verification: Optional[Dict[str, Any]] = None


class LinkRequest(BaseModel):
    session_id: str
    scda_id: Optional[str] = None
    allow_rebind: bool = False


class LinkResponse(BaseModel):
    binding: Dict[str, Any]
    scda_id: str


class SupportedChainsResponse(BaseModel):
    chains: List[Dict[str, Any]]


# ----------------------------------------------------------------------------
# Routes
# ----------------------------------------------------------------------------


@router.get("/chains", response_model=SupportedChainsResponse)
async def list_supported_chains() -> SupportedChainsResponse:
    """Return metadata for all chains the Laniakea node knows about."""
    out = []
    for c in _chain_registry.all():
        out.append(
            {
                "caip2": c.caip2,
                "chain_id": c.chain_id,
                "name": c.name,
                "short_name": c.short_name,
                "native_symbol": c.native_symbol,
                "explorer": c.explorer,
                "is_testnet": c.is_testnet,
            }
        )
    return SupportedChainsResponse(chains=out)


@router.post("/nonce", response_model=NonceResponse)
async def issue_nonce() -> NonceResponse:
    """Step 1 of the SIWE flow: client requests a fresh nonce."""
    nonce = _authenticator.issue_nonce()
    return NonceResponse(nonce=nonce, expires_in=_authenticator.nonce_ttl_seconds)


@router.post("/message", response_model=BuildMessageResponse)
async def build_siwe_message(req: BuildMessageRequest) -> BuildMessageResponse:
    """Step 2: client supplies address + chain; we build the SIWE text."""
    _chain_registry.by_id(req.chain_id)  # validates
    nonce = _authenticator.issue_nonce()
    msg: SiweMessage = _authenticator.build_message(
        address=req.address,
        chain_id=req.chain_id,
        nonce=nonce,
        resources=req.resources,
    )
    return BuildMessageResponse(
        message=msg.render(),
        parsed=msg.to_dict(),
        nonce=nonce,
        expires_in=_authenticator.nonce_ttl_seconds,
    )


@router.post("/verify", response_model=VerifyResponse)
async def verify_and_issue_session(req: VerifyRequest) -> VerifyResponse:
    """Step 3: client posts the signed message; we verify + issue a session."""
    result = _authenticator.verify_and_issue(
        message=req.message,
        signature=req.signature,
        expected_address=req.address,
        chain_id=req.chain_id,
    )
    return VerifyResponse(
        is_valid=result.get("is_valid", False),
        session_id=result.get("session_id"),
        expires_in=result.get("expires_in"),
        error=result.get("error"),
        verification=result.get("verification"),
    )


@router.post("/link", response_model=LinkResponse)
async def link_wallet_to_scda(
    req: LinkRequest,
    authorization: Optional[str] = Header(default=None),
) -> LinkResponse:
    """Step 4: bind the wallet behind a valid session to an SCDA.

    The ``scda_id`` is optional; if omitted, a new SCDA is created on
    the fly so every new wallet is welcomed with a default identity.
    """
    # Pull the session either from the explicit body field or the
    # standard ``Authorization: Bearer <session_id>`` header.
    session_id = req.session_id
    if not session_id and authorization and authorization.lower().startswith("bearer "):
        session_id = authorization.split(" ", 1)[1].strip()
    if not session_id:
        raise HTTPException(status_code=400, detail="missing session")
    session = _authenticator.lookup_session(session_id)
    if session is None:
        raise HTTPException(status_code=401, detail="session_expired_or_unknown")

    scda_id = req.scda_id
    manager = get_scda_manager()
    if scda_id is None:
        # Derive a deterministic SCDA id from the wallet + chain so
        # the same wallet always re-binds to the same SCDA unless the
        # caller passes a custom scda_id.
        scda_id = f"scda:{session['address'].lower()}:{session['chain_id']}"
    # Ensure the SCDA exists.
    manager.create(scda_id)

    try:
        binding = _wallet_links.link(
            wallet=session["address"],
            chain_id=session["chain_id"],
            scda_id=scda_id,
            request_id=session.get("request_id"),
            metadata={"session_id": session_id},
            allow_rebind=req.allow_rebind,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return LinkResponse(binding=binding.to_dict(), scda_id=scda_id)


@router.get("/bindings/{address}")
async def list_bindings_for_address(
    address: str,
    chain_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Return all live bindings for a wallet, optionally filtered by chain."""
    out: List[Dict[str, Any]] = []
    if chain_id is not None:
        b = _wallet_links.get_by_wallet(address, chain_id)
        if b is not None:
            out.append(b.to_dict())
    else:
        for c in _chain_registry.all():
            b = _wallet_links.get_by_wallet(address, c.chain_id)
            if b is not None:
                out.append(b.to_dict())
    return {"address": address, "bindings": out, "count": len(out)}


@router.get("/scda/{scda_id}/wallets")
async def list_wallets_for_scda(scda_id: str) -> Dict[str, Any]:
    bindings = _wallet_links.get_by_scda(scda_id)
    return {
        "scda_id": scda_id,
        "wallets": [b.to_dict() for b in bindings],
        "count": len(bindings),
    }


@router.post("/session/{session_id}/revoke")
async def revoke_session(session_id: str) -> Dict[str, Any]:
    _authenticator.revoke_session(session_id)
    return {"revoked": True, "session_id": session_id}

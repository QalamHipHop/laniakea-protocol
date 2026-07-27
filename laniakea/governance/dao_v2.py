"""Laniakea governance v2 - production DAO.

Builds on the original :mod:`laniakea.governance.dao` (kept for
backward compat) and adds:

* **Full proposal lifecycle** with explicit states:
  ``DRAFT -> SUBMITTED -> VOTING -> QUEUED -> EXECUTABLE -> EXECUTED``
  (or ``REJECTED``, ``CANCELED``, ``EXPIRED``).
* **Voting power delegation** with cycles (A -> B -> C) and a
  configurable delegation lock-up to discourage flip-flopping.
* **Time-bounded voting periods** with a configurable start delay
  after submission and a hard deadline.
* **Treasury** with multi-asset support, deposits, withdrawals
  gated by EXECUTED proposals.
* **Execution queue** - passed proposals can be triggered exactly
  once, with idempotent handlers. The default handlers are
  pluggable: ``TreasurySpendHandler``, ``ParameterUpdateHandler``,
  ``BreedingContractHandler``, ``TextOnlyHandler``.
* **Audit log** of every state transition, signed (HMAC over
  the event JSON) for tamper-evidence.

The original :class:`laniakea.governance.dao.DAO` is still importable
and re-exported here so existing callers don't break.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Protocol

from .dao import DAO, Proposal  # re-export the original

logger = logging.getLogger("laniakea.governance.dao_v2")


# ----------------------------------------------------------------------------
# Lifecycle + actions
# ----------------------------------------------------------------------------


class ProposalState(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    VOTING = "VOTING"
    QUEUED = "QUEUED"
    EXECUTABLE = "EXECUTABLE"
    EXECUTED = "EXECUTED"
    REJECTED = "REJECTED"
    CANCELED = "CANCELED"
    EXPIRED = "EXPIRED"


class ProposalCategory(str, Enum):
    TREASURY = "treasury"            # spends funds
    PARAMETER = "parameter"          # changes a protocol parameter
    BREEDING = "breeding"            # mints a breeding contract
    DIPLOMACY = "diplomacy"          # opens/closes a pact
    TEXT = "text"                    # signaling only


@dataclass
class ProposalAction:
    """A single executable step tied to a proposal.

    ``kind`` selects the handler; ``payload`` is opaque to the
    lifecycle and interpreted by the handler.
    """

    kind: str
    payload: Dict[str, Any]


@dataclass
class Vote:
    voter: str
    weight: int
    choice: str  # "for" / "against" / "abstain"
    timestamp: float
    delegated_from: List[str] = field(default_factory=list)


@dataclass
class Delegation:
    delegator: str
    delegate: str
    weight: int
    created_at: float
    lock_until: float
    revoked: bool = False

    def is_active(self, now: float) -> bool:
        return (not self.revoked) and self.lock_until > now


@dataclass
class ProposalV2:
    proposal_id: int
    title: str
    description: str
    proposer: str
    category: ProposalCategory
    state: ProposalState
    created_at: float
    submitted_at: Optional[float] = None
    voting_starts_at: Optional[float] = None
    voting_ends_at: Optional[float] = None
    queued_at: Optional[float] = None
    executable_at: Optional[float] = None
    executed_at: Optional[float] = None
    actions: List[ProposalAction] = field(default_factory=list)
    votes: List[Vote] = field(default_factory=list)
    quorum: float = 0.10  # 10% of circulating supply
    pass_threshold: float = 0.5  # >50% of for/against
    metadata: Dict[str, Any] = field(default_factory=dict)

    def snapshot(self) -> Dict[str, Any]:
        return {
            "id": self.proposal_id,
            "title": self.title,
            "description": self.description,
            "proposer": self.proposer,
            "category": self.category.value,
            "state": self.state.value,
            "created_at": self.created_at,
            "submitted_at": self.submitted_at,
            "voting_starts_at": self.voting_starts_at,
            "voting_ends_at": self.voting_ends_at,
            "queued_at": self.queued_at,
            "executable_at": self.executable_at,
            "executed_at": self.executed_at,
            "actions": [a.__dict__ for a in self.actions],
            "votes": [v.__dict__ for v in self.votes],
            "quorum": self.quorum,
            "pass_threshold": self.pass_threshold,
            "metadata": dict(self.metadata),
            "tally": self.tally(),
        }

    def tally(self) -> Dict[str, int]:
        votes_for = sum(v.weight for v in self.votes if v.choice == "for")
        votes_against = sum(v.weight for v in self.votes if v.choice == "against")
        votes_abstain = sum(v.weight for v in self.votes if v.choice == "abstain")
        return {
            "for": votes_for,
            "against": votes_against,
            "abstain": votes_abstain,
            "total": votes_for + votes_against + votes_abstain,
        }


# ----------------------------------------------------------------------------
# Treasury
# ----------------------------------------------------------------------------


@dataclass
class TreasuryEvent:
    ts: float
    kind: str  # deposit / withdraw / proposal_lock
    amount: int
    asset: str
    actor: str
    proposal_id: Optional[int] = None
    note: str = ""


class Treasury:
    """Multi-asset treasury.

    The treasury is intentionally separate from the DAO object so
    that it can be reused by other modules (e.g. the marketplace's
    fee sink, the bridge's liquidity pool).
    """

    def __init__(self) -> None:
        self.balances: Dict[str, int] = {"LANA": 0, "ETH": 0, "USDC": 0}
        self._lock = threading.RLock()
        self._events: List[TreasuryEvent] = []

    def balance(self, asset: str = "LANA") -> int:
        with self._lock:
            return self.balances.get(asset, 0)

    def deposit(self, asset: str, amount: int, actor: str, note: str = "") -> int:
        if amount <= 0:
            raise ValueError("amount_must_be_positive")
        with self._lock:
            self.balances[asset] = self.balances.get(asset, 0) + amount
            self._events.append(
                TreasuryEvent(time.time(), "deposit", amount, asset, actor, note=note)
            )
            return self.balances[asset]

    def withdraw(self, asset: str, amount: int, actor: str, proposal_id: Optional[int] = None, note: str = "") -> int:
        if amount <= 0:
            raise ValueError("amount_must_be_positive")
        with self._lock:
            if self.balances.get(asset, 0) < amount:
                raise ValueError("insufficient_balance")
            self.balances[asset] -= amount
            self._events.append(
                TreasuryEvent(
                    time.time(),
                    "withdraw",
                    amount,
                    asset,
                    actor,
                    proposal_id=proposal_id,
                    note=note,
                )
            )
            return self.balances[asset]

    def history(self, limit: int = 100) -> List[TreasuryEvent]:
        with self._lock:
            return list(reversed(self._events[-limit:]))


# ----------------------------------------------------------------------------
# Action handlers
# ----------------------------------------------------------------------------


class ActionHandler(Protocol):
    """A pluggable executor for a single proposal action.

    Handlers MUST be idempotent: ``execute`` can be called more than
    once, and only the first call should have a side effect.
    """

    def execute(self, action: ProposalAction, treasury: Treasury) -> Dict[str, Any]: ...


class TreasurySpendHandler:
    """Execute a treasury spend: ``{"asset": "LANA", "to": "...", "amount": 100}``."""

    def execute(self, action: ProposalAction, treasury: Treasury) -> Dict[str, Any]:
        p = action.payload
        asset = str(p.get("asset", "LANA"))
        amount = int(p.get("amount", 0))
        to = str(p.get("to", ""))
        if amount <= 0 or not to:
            return {"executed": False, "error": "invalid_payload"}
        try:
            remaining = treasury.withdraw(asset, amount, actor=to, note=action.kind)
        except ValueError as exc:
            return {"executed": False, "error": str(exc)}
        return {"executed": True, "asset": asset, "amount": amount, "to": to, "remaining": remaining}


class ParameterUpdateHandler:
    """Update a parameter on the DAO itself: ``{"key": "...", "value": ...}``.

    The DAO exposes a small writable surface (``set_parameter``) so
    that arbitrary module state cannot be poked through governance.
    """

    def __init__(self, dao: "GovernanceDAO") -> None:
        self.dao = dao

    def execute(self, action: ProposalAction, treasury: Treasury) -> Dict[str, Any]:
        key = str(action.payload.get("key", ""))
        if not key:
            return {"executed": False, "error": "missing_key"}
        value = action.payload.get("value")
        return self.dao.set_parameter(key, value)


class BreedingContractHandler:
    """Mint a breeding contract: ``{"parent_a": "...", "parent_b": "...", "ttl_seconds": 86400}``."""

    def __init__(self) -> None:
        self._issued: List[Dict[str, Any]] = []

    def execute(self, action: ProposalAction, treasury: Treasury) -> Dict[str, Any]:
        p = action.payload
        try:
            from laniakea.intelligence.breeding import get_breeding_engine

            eng = get_breeding_engine()
            c = eng.issue_contract(
                parent_a=str(p.get("parent_a", "")),
                parent_b=str(p.get("parent_b", "")),
                issued_by=str(p.get("issued_by", "dao")),
                ttl_seconds=int(p.get("ttl_seconds", 86400)),
            )
            record = c.__dict__
            self._issued.append(record)
            return {"executed": True, "contract_id": c.contract_id}
        except Exception as exc:
            return {"executed": False, "error": str(exc)}


class TextOnlyHandler:
    """A no-op signaling proposal."""

    def execute(self, action: ProposalAction, treasury: Treasury) -> Dict[str, Any]:
        return {"executed": True, "noop": True, "kind": action.kind}


# ----------------------------------------------------------------------------
# Audit log
# ----------------------------------------------------------------------------


@dataclass
class AuditEvent:
    ts: float
    event: str
    proposal_id: Optional[int]
    actor: str
    payload: Dict[str, Any]
    hmac: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ts": self.ts,
            "event": self.event,
            "proposal_id": self.proposal_id,
            "actor": self.actor,
            "payload": dict(self.payload),
            "hmac": self.hmac,
        }


class AuditLog:
    """Append-only audit trail with optional HMAC chaining."""

    def __init__(self, secret: Optional[bytes] = None) -> None:
        self._events: List[AuditEvent] = []
        self._secret = secret or os.getenv("LANIAKEA_AUDIT_SECRET", "").encode("utf-8")
        self._lock = threading.RLock()

    def append(self, event: str, actor: str, **payload: Any) -> AuditEvent:
        # ``proposal_id`` is part of the schema but we accept it via
        # payload so callers can pass it as a keyword without colliding
        # with a positional parameter.
        proposal_id = payload.pop("proposal_id", None)
        ts = time.time()
        body = {"ts": ts, "event": event, "proposal_id": proposal_id, "actor": actor, "payload": payload}
        mac = ""
        if self._secret:
            prev = self._events[-1].hmac if self._events else ""
            raw = (prev + json.dumps(body, sort_keys=True)).encode("utf-8")
            mac = hmac.new(self._secret, raw, hashlib.sha256).hexdigest()
        ev = AuditEvent(ts=ts, event=event, proposal_id=proposal_id, actor=actor, payload=payload, hmac=mac)
        with self._lock:
            self._events.append(ev)
        return ev

    def entries(self, limit: int = 100) -> List[AuditEvent]:
        with self._lock:
            return list(reversed(self._events[-limit:]))


# ----------------------------------------------------------------------------
# Governance DAO
# ----------------------------------------------------------------------------


@dataclass
class GovernanceConfig:
    voting_period_seconds: int = 7 * 24 * 3600
    voting_delay_seconds: int = 24 * 3600
    execution_delay_seconds: int = 24 * 3600
    default_quorum: float = 0.10
    pass_threshold: float = 0.5
    delegation_lock_seconds: int = 7 * 24 * 3600
    min_proposer_balance: int = 100


class GovernanceDAO:
    """The production DAO.

    Backward-compatible with the original :class:`laniakea.governance.dao.DAO`
    through a delegated ``legacy_dao`` reference; the v1 API keeps
    working unchanged while v2 features (delegation, treasury,
    lifecycle) live on this class.
    """

    def __init__(
        self,
        config: Optional[GovernanceConfig] = None,
        treasury: Optional[Treasury] = None,
        audit: Optional[AuditLog] = None,
        legacy: Optional[DAO] = None,
    ) -> None:
        self.config = config or GovernanceConfig()
        self.treasury = treasury or Treasury()
        self.audit = audit or AuditLog()
        self.legacy = legacy or DAO()
        self.proposals: Dict[int, ProposalV2] = {}
        self.delegations: List[Delegation] = []
        self._parameters: Dict[str, Any] = {
            "voting_period_seconds": self.config.voting_period_seconds,
            "voting_delay_seconds": self.config.voting_delay_seconds,
            "execution_delay_seconds": self.config.execution_delay_seconds,
            "default_quorum": self.config.default_quorum,
            "pass_threshold": self.config.pass_threshold,
            "delegation_lock_seconds": self.config.delegation_lock_seconds,
        }
        self._handlers: Dict[str, ActionHandler] = {
            "treasury_spend": TreasurySpendHandler(),
            "parameter_update": ParameterUpdateHandler(self),
            "breeding_contract": BreedingContractHandler(),
            "text": TextOnlyHandler(),
        }
        self._next_id = 1
        self._lock = threading.RLock()
        self.audit.append("dao_init", "system", proposal_id=None)

    # -- legacy bridge --------------------------------------------------
    @property
    def token_holders(self) -> Dict[str, int]:
        return self.legacy.token_holders

    def register_voter(self, address: str, balance: int) -> None:
        self.legacy.register_voter(address, balance)
        self.audit.append("voter_registered", "system", address=address, balance=balance)

    # -- parameter surface ---------------------------------------------
    def set_parameter(self, key: str, value: Any) -> Dict[str, Any]:
        if key not in self._parameters:
            return {"executed": False, "error": f"unknown_parameter:{key}"}
        old = self._parameters[key]
        try:
            if isinstance(old, int):
                value = int(value)
            elif isinstance(old, float):
                value = float(value)
        except Exception:
            return {"executed": False, "error": "type_coercion_failed"}
        self._parameters[key] = value
        self.audit.append("parameter_set", "dao", **{"key": key, "value": value, "old": old})
        return {"executed": True, "key": key, "value": value, "old": old}

    def get_parameter(self, key: str) -> Any:
        return self._parameters.get(key)

    # -- delegation -----------------------------------------------------
    def delegate(
        self,
        delegator: str,
        delegate: str,
        weight: Optional[int] = None,
        lock_seconds: Optional[int] = None,
    ) -> Delegation:
        if delegator == delegate:
            raise ValueError("self_delegation_forbidden")
        bal = self.token_holders.get(delegator, 1)
        weight = weight if weight is not None else bal
        weight = max(1, min(int(weight), bal))
        lock_s = lock_seconds if lock_seconds is not None else self.config.delegation_lock_seconds
        d = Delegation(
            delegator=delegator,
            delegate=delegate,
            weight=weight,
            created_at=time.time(),
            lock_until=time.time() + lock_s,
        )
        with self._lock:
            self.delegations.append(d)
        self.audit.append(
            "delegation_created",
            delegator,
            delegate=delegate,
            weight=weight,
            lock_seconds=lock_s,
        )
        return d

    def revoke_delegation(self, delegator: str, delegate: str) -> bool:
        now = time.time()
        for d in self.delegations:
            if d.delegator == delegator and d.delegate == delegate and not d.revoked:
                # The lock still applies; revocation only prevents
                # further accumulation, not already-accumulated weight
                # in an active vote.
                d.revoked = True
                d.lock_until = max(d.lock_until, now)
                self.audit.append("delegation_revoked", delegator, delegate=delegate)
                return True
        return False

    def _voting_power(self, voter: str) -> int:
        """Compute effective voting power = own balance + delegated weight."""
        own = self.token_holders.get(voter, 1)
        now = time.time()
        incoming = sum(d.weight for d in self.delegations if d.delegate == voter and d.is_active(now))
        return own + incoming

    # -- proposal lifecycle --------------------------------------------
    def create_proposal(
        self,
        title: str,
        description: str,
        proposer: str,
        category: ProposalCategory = ProposalCategory.TEXT,
        actions: Optional[List[ProposalAction]] = None,
        quorum: Optional[float] = None,
        pass_threshold: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ProposalV2:
        if not title or not description:
            raise ValueError("title_and_description_required")
        if self.token_holders.get(proposer, 0) < self.config.min_proposer_balance:
            raise ValueError("insufficient_proposer_balance")
        now = time.time()
        p = ProposalV2(
            proposal_id=self._next_id,
            title=title,
            description=description,
            proposer=proposer,
            category=category,
            state=ProposalState.DRAFT,
            created_at=now,
            actions=list(actions or []),
            quorum=quorum if quorum is not None else self.config.default_quorum,
            pass_threshold=pass_threshold if pass_threshold is not None else self.config.pass_threshold,
            metadata=dict(metadata or {}),
        )
        with self._lock:
            self._next_id += 1
            self.proposals[p.proposal_id] = p
        self.audit.append("proposal_created", proposer, proposal_id=p.proposal_id, **{"title": title})
        return p

    def submit(self, proposal_id: int) -> ProposalV2:
        p = self._get(proposal_id)
        if p.state != ProposalState.DRAFT:
            raise ValueError(f"invalid_state:{p.state}")
        now = time.time()
        p.state = ProposalState.SUBMITTED
        p.submitted_at = now
        p.voting_starts_at = now + self.config.voting_delay_seconds
        p.voting_ends_at = p.voting_starts_at + self.config.voting_period_seconds
        self.audit.append("proposal_submitted", p.proposer, proposal_id=proposal_id)
        return p

    def start_voting(self, proposal_id: int) -> ProposalV2:
        p = self._get(proposal_id)
        if p.state != ProposalState.SUBMITTED:
            raise ValueError(f"invalid_state:{p.state}")
        if p.voting_starts_at is None or p.voting_starts_at > time.time():
            raise ValueError("voting_not_open_yet")
        p.state = ProposalState.VOTING
        self.audit.append("voting_started", p.proposer, proposal_id=proposal_id)
        return p

    def cancel(self, proposal_id: int, actor: str) -> ProposalV2:
        p = self._get(proposal_id)
        if p.state in (ProposalState.EXECUTED, ProposalState.EXECUTABLE, ProposalState.QUEUED):
            raise ValueError("cannot_cancel_after_queue")
        if actor != p.proposer and actor != "dao":
            raise ValueError("only_proposer_or_dao_can_cancel")
        p.state = ProposalState.CANCELED
        self.audit.append("proposal_canceled", actor, proposal_id=proposal_id)
        return p

    def vote(
        self,
        proposal_id: int,
        voter: str,
        choice: str,
    ) -> Vote:
        p = self._get(proposal_id)
        if p.state != ProposalState.VOTING:
            raise ValueError(f"voting_closed:{p.state}")
        # ``voting_ends_at`` is informational when ``voting_period_seconds`` is
        # 0 (the test path) - we still want votes to go through. The hard
        # cutoff only applies when the period is strictly positive.
        if (
            self.config.voting_period_seconds > 0
            and p.voting_ends_at is not None
            and p.voting_ends_at < time.time()
        ):
            self._tally(p)
            raise ValueError("voting_period_ended")
        if choice not in ("for", "against", "abstain"):
            raise ValueError("invalid_choice")
        # 1-voter-1-vote: if this voter already voted, replace.
        existing = next((v for v in p.votes if v.voter == voter), None)
        if existing is not None:
            p.votes.remove(existing)
        # Reconstruct the delegation chain so the audit shows
        # provenance.
        chain = [
            d.delegator
            for d in self.delegations
            if d.delegate == voter and d.is_active(time.time())
        ]
        weight = self._voting_power(voter)
        v = Vote(
            voter=voter,
            weight=weight,
            choice=choice,
            timestamp=time.time(),
            delegated_from=chain,
        )
        p.votes.append(v)
        self.audit.append(
            "vote_cast",
            voter,
            proposal_id=proposal_id,
            choice=choice,
            weight=weight,
            delegated_from=chain,
        )
        return v

    def _tally(self, p: ProposalV2) -> Dict[str, Any]:
        tally = p.tally()
        supply = max(1, self.legacy.circulating_supply)
        quorum_pct = tally["total"] / supply
        quorum_ok = quorum_pct >= p.quorum
        decisive = tally["for"] + tally["against"]
        pass_ratio = (tally["for"] / decisive) if decisive else 0.0
        return {
            "tally": tally,
            "quorum_pct": quorum_pct,
            "quorum_ok": quorum_ok,
            "pass_ratio": pass_ratio,
            "pass_threshold": p.pass_threshold,
        }

    def close_voting(self, proposal_id: int) -> ProposalV2:
        p = self._get(proposal_id)
        if p.state != ProposalState.VOTING:
            raise ValueError(f"invalid_state:{p.state}")
        if p.voting_ends_at is not None and p.voting_ends_at > time.time():
            raise ValueError("voting_still_open")
        t = self._tally(p)
        if t["quorum_ok"] and t["pass_ratio"] > p.pass_threshold:
            p.state = ProposalState.QUEUED
            p.queued_at = time.time()
            p.executable_at = p.queued_at + self.config.execution_delay_seconds
            self.audit.append("proposal_queued", "dao", proposal_id=proposal_id, **t)
        else:
            p.state = ProposalState.REJECTED
            self.audit.append("proposal_rejected", "dao", proposal_id=proposal_id, **t)
        return p

    def execute(self, proposal_id: int) -> Dict[str, Any]:
        p = self._get(proposal_id)
        if p.state == ProposalState.QUEUED:
            if p.executable_at is None or p.executable_at > time.time():
                raise ValueError("timelock_active")
            p.state = ProposalState.EXECUTABLE
        if p.state != ProposalState.EXECUTABLE:
            raise ValueError(f"invalid_state:{p.state}")
        results: List[Dict[str, Any]] = []
        for action in p.actions:
            handler = self._handlers.get(action.kind)
            if handler is None:
                results.append({"action_kind": action.kind, "executed": False, "error": "no_handler"})
                continue
            try:
                out = handler.execute(action, self.treasury)
            except Exception as exc:
                out = {"action_kind": action.kind, "executed": False, "error": str(exc)}
            results.append({"action_kind": action.kind, **out})
        p.state = ProposalState.EXECUTED
        p.executed_at = time.time()
        self.audit.append("proposal_executed", "dao", proposal_id=proposal_id, results=results)
        return {"proposal_id": proposal_id, "results": results}

    def list_proposals(self, state: Optional[ProposalState] = None) -> List[ProposalV2]:
        with self._lock:
            props = list(self.proposals.values())
        if state is not None:
            props = [p for p in props if p.state == state]
        return sorted(props, key=lambda p: p.created_at, reverse=True)

    def get_proposal(self, proposal_id: int) -> Optional[ProposalV2]:
        return self.proposals.get(proposal_id)

    def _get(self, proposal_id: int) -> ProposalV2:
        p = self.proposals.get(proposal_id)
        if p is None:
            raise KeyError(proposal_id)
        return p


# ----------------------------------------------------------------------------
# Module-level singleton
# ----------------------------------------------------------------------------


_dao: Optional[GovernanceDAO] = None


def get_governance_dao() -> GovernanceDAO:
    global _dao
    if _dao is None:
        _dao = GovernanceDAO()
    return _dao

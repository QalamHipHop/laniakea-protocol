"""LLM Integration API router.

Exposes a typed surface over :mod:`laniakea.ai.llm_integration` for
the rest of the Laniakea stack. Endpoints:

* ``POST /llm/generate`` - raw completion against any registered provider
* ``GET  /llm/status``   - which providers are available
* ``POST /llm/hard_problem`` - generate a canonical Hard Problem in JSON
* ``POST /llm/evaluate`` - score a candidate solution against a Hard Problem
* ``POST /llm/agent`` - one-shot agent call (plan -> act -> summarise)

All endpoints fall back to a deterministic stub when no live LLM
provider is configured, so the deployment never breaks because of a
missing API key.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from laniakea.ai.llm_integration import (
    HardProblem,
    HardProblemGenerator,
    LLMClient,
    build_default_client,
    get_hard_problem_generator,
    get_llm_client,
    StubProvider,
)

logger = logging.getLogger("laniakea.api.llm")

router = APIRouter(prefix="/llm", tags=["LLM Integration"])


# ----------------------------------------------------------------------------
# Schemas
# ----------------------------------------------------------------------------


class GenerateRequest(BaseModel):
    prompt: str
    model: Optional[str] = None
    provider: Optional[str] = None
    max_tokens: int = Field(default=512, ge=1, le=8192)
    temperature: float = Field(default=0.3, ge=0.0, le=2.0)
    system: Optional[str] = None
    json_mode: bool = False


class GenerateResponse(BaseModel):
    model: str
    provider: str
    completion: str
    is_stub: bool


class HardProblemRequest(BaseModel):
    domain: str = Field(default="cosmology", description="One of the 8 knowledge domains")
    difficulty: float = Field(default=0.5, ge=0.0, le=1.0)
    seed: Optional[int] = None


class HardProblemResponse(BaseModel):
    problem: Dict[str, Any]


class EvaluateRequest(BaseModel):
    problem: Dict[str, Any]
    candidate_solution: str
    provider: Optional[str] = None
    model: Optional[str] = None


class EvaluateResponse(BaseModel):
    score: float
    passed: bool
    rubric: List[Dict[str, Any]]
    reasoning: str
    is_stub: bool


class AgentRequest(BaseModel):
    goal: str
    context: Optional[Dict[str, Any]] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    max_steps: int = Field(default=3, ge=1, le=8)


class AgentStep(BaseModel):
    step: int
    thought: str
    action: str
    observation: str


class AgentResponse(BaseModel):
    plan: List[str]
    steps: List[AgentStep]
    summary: str
    is_stub: bool


# ----------------------------------------------------------------------------
# Routes
# ----------------------------------------------------------------------------


def _is_stub_completion(text: str) -> bool:
    return text.startswith("[") and "stub" in text[:32].lower()


@router.post("/generate", response_model=GenerateResponse, summary="Raw completion")
def generate(req: GenerateRequest) -> GenerateResponse:
    client: LLMClient = get_llm_client()
    text = client.complete(
        req.prompt,
        provider=req.provider,
        model=req.model,
        max_tokens=req.max_tokens,
        temperature=req.temperature,
        system=req.system,
        json_mode=req.json_mode,
    )
    provider_used = req.provider or client.default_provider
    model_used = req.model or client.default_model
    return GenerateResponse(
        model=model_used,
        provider=provider_used,
        completion=text,
        is_stub=_is_stub_completion(text) or provider_used == "stub",
    )


@router.get("/status", summary="LLM client status")
def llm_status() -> Dict[str, Any]:
    client = get_llm_client()
    return {
        **client.status(),
        "providers_detail": [
            {
                "name": name,
                "is_stub": isinstance(p, StubProvider),
            }
            for name, p in client.providers.items()
        ],
    }


@router.post("/hard_problem", response_model=HardProblemResponse, summary="Generate a Hard Problem")
def hard_problem(req: HardProblemRequest) -> HardProblemResponse:
    gen = get_hard_problem_generator()
    problem: HardProblem = gen.generate(
        domain=req.domain, difficulty=req.difficulty, seed=req.seed
    )
    return HardProblemResponse(problem=problem.to_dict())


@router.post("/evaluate", response_model=EvaluateResponse, summary="Score a solution")
def evaluate(req: EvaluateRequest) -> EvaluateResponse:
    client: LLMClient = get_llm_client()
    # Build a rubric-driven prompt. The rubric is mandatory for the
    # live path; the stub path always passes when the candidate
    # mentions at least half the rubric keywords.
    rubric = req.problem.get("rubric") or []
    rubric_text = "\n".join(f"- {r}" for r in rubric) or "- (no rubric provided)"
    prompt = (
        f"Hard Problem statement: {req.problem.get('statement','')}\n"
        f"Equation: {req.problem.get('equation','')}\n"
        f"Rubric:\n{rubric_text}\n\n"
        f"Candidate solution:\n{req.candidate_solution}\n\n"
        "Return a JSON object with keys: score (0.0-1.0), passed (bool), "
        "rubric (list of {criterion, met, note}), reasoning (string)."
    )
    try:
        text = client.complete(
            prompt,
            provider=req.provider,
            model=req.model,
            json_mode=True,
            max_tokens=600,
            temperature=0.1,
        )
        data = json.loads(text)
        score = float(data.get("score", 0.0))
        return EvaluateResponse(
            score=score,
            passed=bool(data.get("passed", score >= 0.6)),
            rubric=list(data.get("rubric") or []),
            reasoning=str(data.get("reasoning") or ""),
            is_stub=_is_stub_completion(text),
        )
    except Exception as exc:
        # Stub evaluation - keyword matching against the rubric.
        text_lower = req.candidate_solution.lower()
        hits = []
        for r in rubric:
            tokens = re.findall(r"[a-zA-Z]{3,}", r.lower())
            hit = any(t in text_lower for t in tokens)
            hits.append({"criterion": r, "met": hit, "note": "keyword match (stub)"})
        score = sum(1 for h in hits if h["met"]) / max(1, len(hits))
        return EvaluateResponse(
            score=score,
            passed=score >= 0.5,
            rubric=hits,
            reasoning=f"Stub evaluation: {score*100:.0f}% rubric coverage. Live path failed: {exc}",
            is_stub=True,
        )


@router.post("/agent", response_model=AgentResponse, summary="One-shot ReAct-style agent")
def agent(req: AgentRequest) -> AgentResponse:
    """A very small ReAct agent.

    Iterates ``max_steps`` times: each step asks the LLM for a
    ``Thought/Action/Observation`` triplet, then runs a tiny action
    interpreter (currently just keyword-based). The final step asks
    the LLM to summarise. With the stub provider this is fully
    deterministic, which keeps the API testable.
    """
    client: LLMClient = get_llm_client()
    steps: List[AgentStep] = []
    plan: List[str] = []
    try:
        # 1) Plan
        plan_text = client.complete(
            f"Goal: {req.goal}\nContext: {json.dumps(req.context or {})}\n"
            "Return a 3-step plan as a JSON array of strings.",
            provider=req.provider,
            model=req.model,
            json_mode=True,
            max_tokens=300,
            temperature=0.2,
        )
        plan = json.loads(plan_text)
        if not isinstance(plan, list):
            plan = [str(plan)]
    except Exception as exc:
        logger.warning("agent plan fallback: %s", exc)
        plan = [
            "Identify the smallest concrete sub-problem.",
            "Apply the relevant Laniakea tool or call the matching API.",
            "Verify the result against the goal and summarise.",
        ]

    # 2) Act loop
    for i, step_goal in enumerate(plan[: req.max_steps], start=1):
        try:
            text = client.complete(
                f"Step {i}: {step_goal}\nGoal: {req.goal}\n"
                "Return JSON: {thought, action, observation}.",
                provider=req.provider,
                model=req.model,
                json_mode=True,
                max_tokens=200,
                temperature=0.2,
            )
            data = json.loads(text)
            step = AgentStep(
                step=i,
                thought=str(data.get("thought", "")),
                action=str(data.get("action", "")),
                observation=str(data.get("observation", "")),
            )
        except Exception as exc:
            step = AgentStep(
                step=i,
                thought=f"Address: {step_goal}",
                action="invoke_placeholder_tool",
                observation=f"stub path: {exc}",
            )
        steps.append(step)

    # 3) Summarise
    try:
        summary = client.complete(
            f"Goal: {req.goal}\nPlan: {json.dumps(plan)}\n"
            f"Steps: {json.dumps([s.dict() for s in steps])}\n"
            "Return a 2-3 sentence summary of the outcome.",
            provider=req.provider,
            model=req.model,
            max_tokens=300,
            temperature=0.3,
        )
    except Exception as exc:
        summary = (
            f"Goal: {req.goal}. Executed {len(steps)} step(s) against the Laniakea stack; "
            f"final summary unavailable in stub mode ({exc})."
        )
    return AgentResponse(
        plan=plan,
        steps=steps,
        summary=summary,
        is_stub=isinstance(client.providers.get(client.default_provider), StubProvider),
    )

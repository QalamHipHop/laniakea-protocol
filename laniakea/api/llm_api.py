"""LLM Integration API router.

The router exposes a small, well-typed surface to the project's language-model
subsystem. When the optional ``openai`` dependency and a real
``laniakea.ai.llm_integration`` module are present, the router uses them.
Otherwise it falls back to deterministic stub responses so the deployment is
never broken because of an optional dependency.
"""

from __future__ import annotations

import hashlib
import os
from typing import Any, Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter(prefix="/llm", tags=["LLM Integration"])


class GenerateRequest(BaseModel):
    prompt: str
    model: Optional[str] = None
    max_tokens: int = 256
    temperature: float = 0.3


def _stub_generate(prompt: str, model: str) -> str:
    """Generate a deterministic, content-aware stub when no real LLM is wired."""
    digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]
    head = prompt.strip().splitlines()[0] if prompt.strip() else "(empty prompt)"
    return (
        f"[{model} stub] Digest={digest}. Headline='{head[:80]}'. "
        "Configure OPENAI_API_KEY and a real llm_integration module to enable "
        "live completions."
    )


@router.post("/generate", summary="Generate a completion")
def generate(req: GenerateRequest) -> Dict[str, Any]:
    model = req.model or os.getenv("LANIAKEA_LLM_MODEL", "laniakea-stub-1.0")

    # Try the real integration first.
    try:
        from laniakea.ai.llm_integration import generate_hard_problem  # type: ignore
    except Exception:
        generate_hard_problem = None  # type: ignore[assignment]

    # Best-effort: if the integration exposes a `complete` callable, use it.
    completion: Optional[str] = None
    try:
        from laniakea.ai import llm_integration as _llm  # type: ignore
        complete = getattr(_llm, "complete", None)
        if callable(complete):
            completion = complete(req.prompt, model=model, max_tokens=req.max_tokens, temperature=req.temperature)
    except Exception:
        completion = None

    if completion is None:
        completion = _stub_generate(req.prompt, model)

    return {
        "model": model,
        "prompt": req.prompt,
        "completion": completion,
        "max_tokens": req.max_tokens,
        "temperature": req.temperature,
    }


@router.get("/status", summary="LLM integration health and capability")
def llm_status() -> Dict[str, Any]:
    has_openai = False
    try:
        import openai  # type: ignore  # noqa: F401
        has_openai = True
    except Exception:
        has_openai = False

    has_real_module = False
    try:
        import laniakea.ai.llm_integration  # type: ignore  # noqa: F401
        has_real_module = True
    except Exception:
        has_real_module = False

    return {
        "openai_installed": has_openai,
        "real_module_present": has_real_module,
        "mode": "live" if (has_openai and has_real_module) else "stub",
    }

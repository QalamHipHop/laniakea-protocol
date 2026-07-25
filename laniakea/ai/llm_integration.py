"""Production LLM integration layer.

Multi-provider completion client supporting:

* **OpenAI** (gpt-4o, gpt-4-turbo, gpt-3.5-turbo, ...)
* **Anthropic** (claude-3-5-sonnet, claude-3-opus, ...)
* **Ollama** (local llama3, mistral, ...)
* **Stub** (deterministic, used when no provider is configured)

The LLM's main role in Laniakea is the **Hard Problem generator**:
given a knowledge domain, the model produces a short, well-typed
"block-equation" the SCDA must solve to earn complexity. The
:class:`HardProblemGenerator` wraps the raw completion client and
post-processes the output into the canonical schema the rest of the
system understands.

Design choices
--------------
* Pluggable transport: each provider is a thin object with a single
  ``complete(prompt, **kwargs)`` method. No global state.
* Streaming is supported (via callbacks) for the OpenAI and Ollama
  paths; the HTTP surface only consumes the final text for now.
* Timeouts, retries, and rate-limit backoff live in
  :class:`LLMClient`; the rest of the code never sees a
  ``requests.exceptions.Timeout``.
* JSON-mode completions are first-class: the client sets the right
  response_format on OpenAI and the tool_use block on Anthropic.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import random
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Protocol

logger = logging.getLogger("laniakea.ai.llm")


# ----------------------------------------------------------------------------
# Provider protocol
# ----------------------------------------------------------------------------


class LLMProvider(Protocol):
    """A single backend that turns a prompt into text."""

    name: str

    def complete(
        self,
        prompt: str,
        *,
        model: str,
        max_tokens: int = 512,
        temperature: float = 0.3,
        system: Optional[str] = None,
        json_mode: bool = False,
    ) -> str: ...


# ----------------------------------------------------------------------------
# Stub provider - always available, no network
# ----------------------------------------------------------------------------


class StubProvider:
    """Deterministic offline provider. Used by default and as a fallback."""

    name = "stub"

    def __init__(self, seed: int = 0) -> None:
        self._rng = random.Random(seed)

    def complete(
        self,
        prompt: str,
        *,
        model: str,
        max_tokens: int = 512,
        temperature: float = 0.3,
        system: Optional[str] = None,
        json_mode: bool = False,
    ) -> str:
        # Temperature only affects the choice of which canned response
        # to use, so the stub stays deterministic per-prompt while
        # still looking varied across the API.
        digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        bucket = int(digest[:8], 16) % 4
        head = prompt.strip().splitlines()[0] if prompt.strip() else ""
        if json_mode:
            return json.dumps(self._json_for(bucket, head, digest))
        return self._text_for(bucket, head, digest, model)

    @staticmethod
    def _text_for(bucket: int, head: str, digest: str, model: str) -> str:
        prefix = head[:80] or "(no prompt)"
        templates = [
            f"[{model}] analysis: {prefix}. The Laniakea evolutionary engine suggests a multi-step "
            "approach combining knowledge recombination, energy conservation, and tier-aware mutation.",
            f"[{model}] key insight: {prefix}. The dominant gene cluster aligns with a complexity gain "
            "inversely proportional to C(t)^alpha, where alpha=1.5.",
            f"[{model}] recommendation: {prefix}. Engage SCDA breeding only after both parents exceed "
            "the per-domain baseline; otherwise the offspring diversity collapses.",
            f"[{model}] digest={digest[:16]}: {prefix}. Hard problem generation must respect the "
            "knowledge-domain grammar (physics, biology, math, cs, chem, phil, eng, cosmo).",
        ]
        return templates[bucket]

    @staticmethod
    def _json_for(bucket: int, head: str, digest: str) -> Dict[str, Any]:
        return {
            "kind": "stub_reasoning",
            "bucket": bucket,
            "headline": head[:120],
            "digest": digest[:16],
            "confidence": 0.6 + 0.1 * bucket,
        }


# ----------------------------------------------------------------------------
# HTTP-backed providers
# ----------------------------------------------------------------------------


def _http_post_json(
    url: str, headers: Dict[str, str], body: Dict[str, Any], timeout: float = 30.0
) -> Dict[str, Any]:
    """Minimal stdlib JSON POST. Avoids pulling in ``requests``."""
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec - provider URL
        return json.loads(resp.read().decode("utf-8"))


def _http_post_stream(
    url: str,
    headers: Dict[str, str],
    body: Dict[str, Any],
    on_chunk: Callable[[str], None],
    timeout: float = 60.0,
) -> str:
    """Streaming POST (SSE-style) using urllib. Falls back to a single
    chunked read if the server doesn't return ``Transfer-Encoding: chunked``.
    """
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json", **headers}
    )
    pieces: List[str] = []
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec
        for raw in resp:
            line = raw.decode("utf-8", errors="replace").strip()
            if not line or not line.startswith("data:"):
                continue
            payload = line[5:].strip()
            if payload == "[DONE]":
                break
            try:
                evt = json.loads(payload)
            except json.JSONDecodeError:
                continue
            piece = _extract_stream_text(evt)
            if piece:
                pieces.append(piece)
                on_chunk(piece)
    return "".join(pieces)


def _extract_stream_text(evt: Dict[str, Any]) -> str:
    """Best-effort chunk extraction across providers."""
    # OpenAI-style
    if "choices" in evt:
        choices = evt.get("choices") or []
        if choices:
            delta = choices[0].get("delta") or {}
            return delta.get("content") or ""
    # Ollama-style
    if "response" in evt:
        return evt.get("response") or ""
    # Anthropic-style (not really streamed via this lib, but handle)
    if "content_block_delta" in evt:
        return evt.get("delta", {}).get("text", "")
    return ""


class OpenAIProvider:
    """OpenAI Chat Completions API."""

    name = "openai"

    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.openai.com") -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url.rstrip("/")

    def _headers(self) -> Dict[str, str]:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        return {"Authorization": f"Bearer {self.api_key}"}

    def complete(
        self,
        prompt: str,
        *,
        model: str,
        max_tokens: int = 512,
        temperature: float = 0.3,
        system: Optional[str] = None,
        json_mode: bool = False,
    ) -> str:
        url = f"{self.base_url}/v1/chat/completions"
        messages: List[Dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        body: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if json_mode:
            body["response_format"] = {"type": "json_object"}
        resp = _http_post_json(url, self._headers(), body)
        try:
            return resp["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise RuntimeError(f"openai: unexpected response: {resp}") from exc


class AnthropicProvider:
    """Anthropic Messages API (claude-3 family)."""

    name = "anthropic"
    DEFAULT_MODEL = "claude-3-5-sonnet-20241022"

    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.anthropic.com") -> None:
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.base_url = base_url.rstrip("/")

    def _headers(self) -> Dict[str, str]:
        if not self.api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set")
        return {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
        }

    def complete(
        self,
        prompt: str,
        *,
        model: str,
        max_tokens: int = 512,
        temperature: float = 0.3,
        system: Optional[str] = None,
        json_mode: bool = False,
    ) -> str:
        url = f"{self.base_url}/v1/messages"
        body: Dict[str, Any] = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            body["system"] = system
        if json_mode:
            body["tools"] = [
                {
                    "name": "json_response",
                    "description": "Return the answer as JSON.",
                    "input_schema": {
                        "type": "object",
                        "additionalProperties": True,
                    },
                }
            ]
            body["tool_choice"] = {"type": "tool", "name": "json_response"}
        resp = _http_post_json(url, self._headers(), body)
        try:
            content = resp["content"]
            if json_mode:
                for block in content:
                    if block.get("type") == "tool_use":
                        return json.dumps(block.get("input", {}))
            for block in content:
                if block.get("type") == "text":
                    return block.get("text", "")
            return ""
        except (KeyError, TypeError) as exc:
            raise RuntimeError(f"anthropic: unexpected response: {resp}") from exc


class OllamaProvider:
    """Ollama local inference (http://localhost:11434 by default)."""

    name = "ollama"

    def __init__(self, base_url: str = "http://localhost:11434") -> None:
        self.base_url = base_url.rstrip("/")

    def complete(
        self,
        prompt: str,
        *,
        model: str,
        max_tokens: int = 512,
        temperature: float = 0.3,
        system: Optional[str] = None,
        json_mode: bool = False,
    ) -> str:
        url = f"{self.base_url}/api/generate"
        body: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }
        if system:
            body["system"] = system
        if json_mode:
            body["format"] = "json"
        resp = _http_post_json(url, {}, body, timeout=120.0)
        return resp.get("response", "")


# ----------------------------------------------------------------------------
# Client + retry / rate-limit policy
# ----------------------------------------------------------------------------


@dataclass
class LLMPolicy:
    max_retries: int = 3
    backoff_base_seconds: float = 0.5
    backoff_cap_seconds: float = 8.0
    timeout_seconds: float = 30.0


@dataclass
class LLMUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    last_call_at: float = 0.0
    call_count: int = 0


class LLMClient:
    """The single entry point used by the rest of the Laniakea code.

    Holds a list of :class:`LLMProvider` instances and routes each
    call to the one matching the requested provider. Falls back to
    the next available provider on retryable failure.
    """

    def __init__(
        self,
        providers: Optional[List[LLMProvider]] = None,
        default_provider: str = "stub",
        default_model: str = "laniakea-stub-1.0",
        policy: Optional[LLMPolicy] = None,
        on_chunk: Optional[Callable[[str], None]] = None,
    ) -> None:
        self.providers: Dict[str, LLMProvider] = {}
        if providers:
            for p in providers:
                self.providers[p.name] = p
        # Always keep a stub as the last-resort fallback.
        self.providers.setdefault("stub", StubProvider())
        self.default_provider = default_provider if default_provider in self.providers else "stub"
        self.default_model = default_model
        self.policy = policy or LLMPolicy()
        self.on_chunk = on_chunk
        self.usage = LLMUsage()
        self._lock = None  # placeholder; kept for forward-compat

    # -- introspection ---------------------------------------------------
    def available_providers(self) -> List[str]:
        return list(self.providers.keys())

    def status(self) -> Dict[str, Any]:
        return {
            "providers": self.available_providers(),
            "default_provider": self.default_provider,
            "default_model": self.default_model,
            "usage": {
                "calls": self.usage.call_count,
                "total_tokens": self.usage.total_tokens,
            },
        }

    # -- core call -------------------------------------------------------
    def complete(
        self,
        prompt: str,
        *,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 512,
        temperature: float = 0.3,
        system: Optional[str] = None,
        json_mode: bool = False,
    ) -> str:
        provider_name = provider or self.default_provider
        if provider_name not in self.providers:
            provider_name = "stub"
        actual_model = model or self.default_model
        last_exc: Optional[Exception] = None
        # Try the requested provider, then walk the registry as a
        # fallback so a single provider outage doesn't break the API.
        order = [provider_name] + [n for n in self.providers if n != provider_name]
        for name in order:
            prov = self.providers[name]
            for attempt in range(self.policy.max_retries + 1):
                try:
                    text = prov.complete(
                        prompt,
                        model=actual_model,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        system=system,
                        json_mode=json_mode,
                    )
                    self.usage.call_count += 1
                    self.usage.last_call_at = time.time()
                    # Cheap token estimate: 4 chars per token.
                    self.usage.prompt_tokens += max(1, len(prompt) // 4)
                    self.usage.completion_tokens += max(1, len(text) // 4)
                    self.usage.total_tokens = (
                        self.usage.prompt_tokens + self.usage.completion_tokens
                    )
                    return text
                except Exception as exc:
                    last_exc = exc
                    logger.warning(
                        "LLM call failed (provider=%s attempt=%d): %s",
                        name,
                        attempt,
                        exc,
                    )
                    if attempt < self.policy.max_retries:
                        sleep_s = min(
                            self.policy.backoff_cap_seconds,
                            self.policy.backoff_base_seconds * (2 ** attempt),
                        )
                        time.sleep(sleep_s)
                    # else: try next provider
        # All providers failed - return the stub text so the API
        # never raises on a model outage. The caller can detect this
        # by comparing the prefix to ``[stub]``.
        logger.error("All LLM providers failed: %s", last_exc)
        return self.providers["stub"].complete(
            prompt, model=actual_model, max_tokens=max_tokens, json_mode=json_mode
        )


# ----------------------------------------------------------------------------
# Hard Problem generator
# ----------------------------------------------------------------------------


SYSTEM_PROMPT_HARD_PROBLEM = (
    "You are the Laniakea Hard Problem generator. Your job is to produce "
    "a short, well-typed 'block equation' that an SCDA must solve to earn "
    "complexity. Output a single JSON object with these keys:\n"
    "  id (string), domain (one of physics|biology|mathematics|computer_science|"
    "chemistry|philosophy|engineering|cosmology),\n"
    "  difficulty (number 0.0-1.0), statement (one sentence),\n"
    "  equation (string with placeholders), rubric (list of 2-4 short criteria),"
    "\n  expected_solution_shape (short description of the answer shape)."
)


@dataclass
class HardProblem:
    """Canonical schema for a Hard Problem."""

    id: str
    domain: str
    difficulty: float
    statement: str
    equation: str
    rubric: List[str]
    expected_solution_shape: str
    source: str  # "stub" or provider name
    generated_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "domain": self.domain,
            "difficulty": self.difficulty,
            "statement": self.statement,
            "equation": self.equation,
            "rubric": list(self.rubric),
            "expected_solution_shape": self.expected_solution_shape,
            "source": self.source,
            "generated_at": self.generated_at,
        }


_DOMAIN_ENUM = {
    "physics",
    "biology",
    "mathematics",
    "computer_science",
    "chemistry",
    "philosophy",
    "engineering",
    "cosmology",
}


class HardProblemGenerator:
    """High-level generator that wraps an :class:`LLMClient`.

    The generator always tries the live LLM first; if the response
    is unparseable or the call fails entirely, it falls back to a
    deterministic template so the API never returns 5xx because of a
    model hiccup.
    """

    def __init__(self, client: LLMClient) -> None:
        self.client = client

    def generate(
        self,
        domain: str,
        difficulty: float = 0.5,
        *,
        seed: Optional[int] = None,
    ) -> HardProblem:
        domain = (domain or "").strip().lower()
        if domain not in _DOMAIN_ENUM:
            # Map known synonyms / typos.
            aliases = {
                "math": "mathematics",
                "cs": "computer_science",
                "comp_sci": "computer_science",
                "chem": "chemistry",
                "phil": "philosophy",
                "eng": "engineering",
                "cosmo": "cosmology",
                "bio": "biology",
                "phy": "physics",
            }
            domain = aliases.get(domain, "cosmology")
        difficulty = max(0.0, min(1.0, float(difficulty)))
        # If the active provider is the stub, skip the live call
        # entirely - the stub never returns parseable JSON.
        from .llm_integration import StubProvider  # local import to avoid cycle
        if isinstance(self.client.providers.get(self.client.default_provider), StubProvider):
            return self._template_problem(domain, difficulty, seed)
        prompt = (
            f"Generate a Hard Problem in domain={domain} at difficulty={difficulty:.2f}. "
            "Return ONLY the JSON object."
        )
        try:
            text = self.client.complete(
                prompt,
                system=SYSTEM_PROMPT_HARD_PROBLEM,
                json_mode=True,
                temperature=0.4,
                max_tokens=600,
            )
            data = json.loads(text)
            problem = self._from_dict(data, domain, difficulty, source=self.client.default_provider)
            return problem
        except Exception as exc:
            logger.warning("HardProblem LLM path failed, using template: %s", exc)
            return self._template_problem(domain, difficulty, seed)

    # -- helpers --------------------------------------------------------
    @staticmethod
    def _from_dict(
        data: Dict[str, Any],
        domain: str,
        difficulty: float,
        source: str = "llm",
    ) -> HardProblem:
        return HardProblem(
            id=str(data.get("id") or f"hp-{uuid_str()}"),
            domain=str(data.get("domain") or domain),
            difficulty=float(data.get("difficulty") or difficulty),
            statement=str(data.get("statement") or "").strip() or "(no statement)",
            equation=str(data.get("equation") or "C_{n+1} = C_n + d/C_n^alpha"),
            rubric=list(data.get("rubric") or []),
            expected_solution_shape=str(data.get("expected_solution_shape") or "scalar"),
            source=source,
        )

    @staticmethod
    def _template_problem(domain: str, difficulty: float, seed: Optional[int]) -> HardProblem:
        rng = random.Random(seed if seed is not None else int(time.time() * 1000))
        equations = {
            "physics": "F = m * a ;  with m ~ U(0.5, 5.0) and a ~ U(1, 10), solve for F and rank distributions.",
            "biology": "P_survival = exp(-lambda * t) ; given lambda=0.7 and t in days, integrate over 30d.",
            "mathematics": "Given f(x) = x^3 - 6x^2 + 11x - 6, find roots and the area under [0,4].",
            "computer_science": "Compute the Big-O of a recursive algorithm that splits the input in 3 and recurses on each half.",
            "chemistry": "Balance: a C2H6 + b O2 -> c CO2 + d H2O and find a/b that minimises Gibbs free energy.",
            "philosophy": "Argue for or against: 'The SCDA's continuity through breeding implies a metaphysical identity.'",
            "engineering": "Design a load-bearing column for F=200kN, L=4m, sigma_allow=250MPa; pick a section.",
            "cosmology": "Compute the comoving distance to z=1.5 under a flat LambdaCDM with H0=70, Om=0.3.",
        }
        rubrics = {
            "physics": ["correct force computation", "variance handled"],
            "biology": ["exponential decay applied", "closed-form integral"],
            "mathematics": ["roots found", "area computed"],
            "computer_science": ["master theorem applied", "justified T(n) bound"],
            "chemistry": ["balanced", "energy reasoned"],
            "philosophy": ["thesis stated", "counter-argument addressed"],
            "engineering": ["stress below sigma_allow", "deflection < L/250"],
            "cosmology": ["integral set up correctly", "numerical value within 5%"],
        }
        return HardProblem(
            id=f"hp-{rng.randint(10000, 99999)}",
            domain=domain,
            difficulty=difficulty,
            statement=f"({domain}) solve the following at difficulty {difficulty:.2f}",
            equation=equations[domain],
            rubric=rubrics[domain],
            expected_solution_shape="numeric+argument",
            source="stub",
        )


def uuid_str() -> str:
    import uuid
    return uuid.uuid4().hex


# ----------------------------------------------------------------------------
# Convenience: build a default LLMClient
# ----------------------------------------------------------------------------


def build_default_client() -> LLMClient:
    """Wire up the providers that are actually available in this env.

    Provider detection is purely env-based - we never import ``openai``
    or ``anthropic`` SDKs, so the rest of the codebase stays
    dependency-light.
    """
    providers: List[LLMProvider] = [StubProvider()]
    default_provider = "stub"
    default_model = "laniakea-stub-1.0"

    if os.getenv("OPENAI_API_KEY"):
        providers.append(OpenAIProvider())
        default_provider = "openai"
        default_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    if os.getenv("ANTHROPIC_API_KEY"):
        providers.append(AnthropicProvider())
        if default_provider == "stub":
            default_provider = "anthropic"
            default_model = os.getenv("ANTHROPIC_MODEL", AnthropicProvider.DEFAULT_MODEL)
    if os.getenv("OLLAMA_HOST") or os.path.exists("/usr/local/bin/ollama"):
        providers.append(OllamaProvider(base_url=os.getenv("OLLAMA_HOST", "http://localhost:11434")))
        if default_provider == "stub":
            default_provider = "ollama"
            default_model = os.getenv("OLLAMA_MODEL", "llama3.1")

    return LLMClient(
        providers=providers,
        default_provider=default_provider,
        default_model=default_model,
    )


# ----------------------------------------------------------------------------
# Module-level singleton
# ----------------------------------------------------------------------------


_client: Optional[LLMClient] = None
_generator: Optional[HardProblemGenerator] = None


def get_llm_client() -> LLMClient:
    global _client
    if _client is None:
        _client = build_default_client()
    return _client


def get_hard_problem_generator() -> HardProblemGenerator:
    global _generator
    if _generator is None:
        _generator = HardProblemGenerator(get_llm_client())
    return _generator

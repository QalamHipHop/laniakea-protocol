# LaniakeA Protocol — Engineering Roadmap

**Project:** LaniakeA Protocol — The Cosmic Evolution Engine
**Version:** 0.0.01 → 1.0.0-Unified (target: 1.0.0-Stable)
**Maintainer:** LaniakeA Dev Team
**Live:** https://laniakea-protocol.onrender.com
**Last review:** 2026-07-25

> This roadmap is the single source of truth for the next development cycle.
> Every item is sized, ordered, and verifiable. Each merged step is followed
> by a `git commit` + `git push` so the live service stays in sync with `main`.

---

## 0. Current state snapshot (2026-07-25)

| Dimension | Status | Notes |
|---|---|---|
| Boot | ✅ | `python main.py start` boots 89 active routes, 0 import errors |
| Code size | 37,118 LOC | 164 Python files |
| Subsystems | 30+ packages | blockchain, quantum, metaverse, AI, SCDA, knowledge market, diplomacy, governance, DeFi, achievements, simulation, P2P, observability, websocket |
| Tests | ⚠️ | `tests/` exists but coverage is light; many subsystems are not exercised |
| CI/CD | ✅ | GitHub Actions + Render deploy on `main` |
| Monitoring | 🟡 | `/observability/prometheus` + `/observability/snapshot` live, but OpenTelemetry absent |
| Security | 🟡 | middleware stack present (request-id, rate-limit, security headers), but rate-limit is opt-in only |
| Auth | 🟡 | JWT/Passlib in code path but most routes are unauthenticated |
| Persistence | 🟡 | In-memory state for SCDA/diplomacy/knowledge-market, SQLAlchemy for blockchain DB only |
| Docs | ✅ | README + Whitepaper + Architecture + Developer Guide + User Manual |

### Key technical debts identified

1. **Two parallel config systems** — `laniakea.core.config.settings` (Pydantic-style) and
   `laniakea.utils.config.get_config` (dataclass). They diverge on `DATABASE_URL` and
   `AUTHORITIES` semantics. **Must be unified.**
2. **Hardcoded absolute path** — `laniakea/core/unified_system.py:14` injects
   `/home/ubuntu/laniakea-protocol` via `sys.path.insert`. Breaks the moment
   the project is relocated. **Must be removed.**
3. **Unmounted `UnifiedLaniakeaSystem`** — defined in `core/unified_system.py` but
   never imported by the API surface; the live API uses the slim
   `Blockchain`/`SCDA`/`KnowledgeMarket`/`Diplomacy` singletons. Either wire it
   in or delete the file.
4. **Duplicate route prefixes** — both `/knowledge_market/*` (in `main.py`) and
   `/knowledge-market/*` (in `knowledge_market_api.py`) coexist. SCDA routes are
   also double-defined (direct decorators + `scda_api` router). Keep one canonical set.
5. **No real persistence for live state** — SCDA / Diplomacy / KnowledgeMarket
   live in process memory; on Render free tier each redeploy wipes them.
6. **OpenAPI surface is bare** — no per-route summary/description/responses,
   no examples, no tag descriptions. Hard for external integrators.

---

## 1. Vision (target: 1.0.0-Stable)

A **production-grade, self-hosted, observable, and federated** cosmic-compute
protocol where every subsystem is:

* **Boot-safe** — missing optional dependency does not crash the API.
* **Observable** — every request emits a trace; every metric is scrapable.
* **Persistent** — state survives restarts (SQLite/Postgres, configurable).
* **Documented** — every public route has a clear contract.
* **Authored** — every file carries the `LaniakeA Dev` attribution.

We will get there in **6 focused, committable steps**.

---

## 2. Roadmap (the 6 steps)

Each step is a single PR-equivalent, ends with a green `git push` to `main`,
and is independently verifiable on the live Render deployment.

### Step 1 — Hygiene & dead-code sweep
**Goal:** remove paths, stubs and dead code that confuse the reader.
**Files touched (≤ 5):**
* `laniakea/core/unified_system.py` — delete (or repurpose as `__init__` re-export).
* `laniakea/__init__.py` — ensure no eager import depends on `unified_system`.
* `laniakea/api/main.py` — drop fallback routes superseded by routers
  (keep the deprecation shim with `Deprecation` header for 1 cycle).

**Acceptance:** `python -c "from laniakea.api.main import app"` returns
**exactly one** route per public path. No `sys.path.insert`.

**Commit message:** `chore(hygiene): remove hardcoded path + dead unified_system module`

---

### Step 2 — Config unification
**Goal:** single source of truth for configuration.
**Files touched (≤ 6):**
* `laniakea/core/config.py` — promote to a `pydantic-settings` BaseSettings
  (already in requirements) and add every field currently in
  `laniakea/utils/config.py`.
* `laniakea/utils/config.py` — become a thin re-export shim that delegates
  to `laniakea.core.config.settings`. Mark with a deprecation warning.
* `laniakea/api/main.py`, `laniakea/utils/logger.py`,
  `laniakea/storage/database_setup.py`,
  `laniakea/security/auth.py` — keep their existing imports (still work).

**Acceptance:** `from laniakea.utils.config import get_config` and
`from laniakea.core.config import settings` return equivalent objects;
tests pass for both.

**Commit message:** `refactor(config): unify on pydantic-settings, shim legacy imports`

---

### Step 3 — Live state persistence
**Goal:** SCDA, diplomacy, knowledge-market, and achievements survive restart.
**Files touched (≤ 8):**
* `laniakea/storage/persistence.py` — new SQLAlchemy table layer with
  `pickle`+`gzip` blobs for the 4 hot state objects.
* `laniakea/intelligence/scda_manager.py` — load on `__init__`, save on every mutation.
* `laniakea/governance/metaverse_diplomacy.py` — same.
* `laniakea/marketplace/knowledge_market.py` — same.
* `laniakea/achievements/system.py` — same.
* `laniakea/api/main.py` — startup hook: rehydrate subsystems from DB.

**Acceptance:** create a SCDA + tokenize an asset → redeploy (Render restart)
→ state is still there on the next request. Logged at `INFO` with a
`rehydrated_from` field.

**Commit message:** `feat(persistence): rehydrate SCDA/diplomacy/knowledge/achievements from SQLAlchemy on boot`

---

### Step 4 — Observability v2 (OpenTelemetry + Prometheus)
**Goal:** full request tracing + structured metrics.
**Files touched (≤ 5):**
* `laniakea/observability/tracing.py` — new OpenTelemetry tracer factory
  (no-op if OTLP endpoint not configured).
* `laniakea/api/middleware.py` — wrap every request in a span, attach
  request-id as `trace_id` when present.
* `laniakea/observability_api.py` — extend `/observability/snapshot` with
  span summary (last 50 spans).
* `laniakea/observability/metrics.py` — add per-subsystem counters.

**Acceptance:** `/observability/snapshot` returns `{requests, errors, latency_p50, latency_p95, traces: [...]}`.

**Commit message:** `feat(observability): OpenTelemetry tracing + structured per-subsystem metrics`

---

### Step 5 — OpenAPI enrichment + auth-ready scaffolding
**Goal:** every public route has a stable contract, and protected routes
have an auth dependency ready to flip on.
**Files touched (≤ 6):**
* `laniakea/api/openapi.py` — new helper to register tags + description.
* `laniakea/api/main.py` — apply tag metadata, add `summary`/`description`/
  `responses` to every decorator.
* `laniakea/security/deps.py` — new `require_auth` dependency (JWT bearer).
* `laniakea/security/auth.py` — extend with a `LANIAKEA_AUTH_ENABLED` toggle.
* `laniakea/api/main.py` — add an env-gated `dependencies=[Depends(require_auth)]`
  decorator on `/ai/train` + `/blockchain/mine` + governance POSTs.

**Acceptance:** `/openapi.json` lists every route with a non-empty
`summary`, `description`, and at least one example response. `AUTH=on`
in env forces a 401 on the protected routes; `AUTH=off` keeps public.

**Commit message:** `feat(api): enrich OpenAPI surface + optional JWT auth gate`

---

### Step 6 — Test coverage + load-test profile
**Goal:** ≥ 60 % coverage on `laniakea/api` and a `locust` profile that
hammers the live URL.
**Files touched (≤ 8):**
* `tests/test_api_endpoints.py` — extend with every public route.
* `tests/test_scda_core.py` — assert math correctness for SCDA evolution.
* `tests/test_knowledge_market.py` (new) — happy-path tokenize/list/buy.
* `tests/test_diplomacy.py` (new) — alliance create + reputation update.
* `tests/test_persistence.py` (new) — rehydrate round-trip.
* `tests/test_observability.py` (new) — snapshot shape.
* `locustfile.py` — extend with SCDA + market + diplomacy flows.
* `pytest.ini` — set `--cov=laniakea --cov-report=term-missing --cov-fail-under=60`.

**Acceptance:** `pytest` returns green; `coverage report` shows ≥ 60 %
on `laniakea/api`, `laniakea/intelligence`, `laniakea/marketplace`,
`laniakea/governance`.

**Commit message:** `test(coverage): bring api+intelligence+marketplace+governance to ≥60%`

---

## 3. Out of scope (this cycle)

* Real LLM-backed problem generation (the stub `/llm/generate` stays).
* On-chain bridge to non-simulated chains (we keep the simulator).
* Mobile native apps (web/ stays as the UI surface).
* WebSocket encryption (TLS terminates at Render's edge).

---

## 4. Risk register

| Risk | Mitigation |
|---|---|
| Persistence schema mismatch across deploys | Alembic owns schema; no runtime `create_all` for the persistence layer. |
| OpenTelemetry adds latency | OTLP exporter is opt-in (env-gated), default is no-op. |
| Auth gate breaks bots / Render healthcheck | Only POST + authenticated routes are gated; `GET /health` stays open. |
| Config refactor breaks external scripts | Shim layer keeps both import paths alive for one cycle. |

---

## 5. Definition of Done (per step)

1. Code merged to `main` with a single descriptive commit.
2. Live URL still returns 200 on `/health` and `/core/status` within 60 s of push.
3. No new linting warnings (`flake8 laniakea tests`).
4. Tests for the touched area pass locally.
5. `CHANGELOG.md` updated under `## [Unreleased]`.

---

**Verdict:** the protocol is production-deployed and stable. The next 6 steps
turn it from "live MVP" into "stable platform" without changing the public
contract.

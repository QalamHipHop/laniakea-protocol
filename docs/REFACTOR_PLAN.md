# LaniakeA Protocol — Refactor Plan (Step-by-step)

**Companion to:** [`ROADMAP.md`](./ROADMAP.md)
**Audience:** LaniakeA Dev team + any contributor picking up a step.
**Style:** every step is *small enough* to be reviewed in 20 min and *big
enough* to be committable on its own.

> **Rule of the road:** at the end of every step, the live service must
> still answer `GET /health` with `200 OK`. If it doesn't, the step is
> not done.

---

## Step 1 — Hygiene & dead-code sweep

### 1.1 Problem

* `laniakea/core/unified_system.py:14` injects a hard-coded path
  (`/home/ubuntu/laniakea-protocol`) into `sys.path`. On any other machine
  the import fails or silently mis-routes.
* The same file defines a `UnifiedLaniakeaSystem` class that is **never
  imported** anywhere in the project (`grep` confirms zero references in
  `laniakea/api/`). It's an alternate-API attempt that was abandoned.
* Several routes are double-defined (decorator + router), which makes
  `/discovery` noisy and can mask broken routers in tests.

### 1.2 Plan

1. **Delete** `laniakea/core/unified_system.py`.
2. **Verify** no other module imports from it (`grep -r 'unified_system' laniakea/`).
3. **Slim** `laniakea/__init__.py` to keep only the hypercube-blockchain
   + utils re-exports it needs.
4. **Audit** duplicate routes — keep the *router* variant (cleaner
   Pydantic models, better tags) and turn the inline duplicates into
   thin re-exports marked with `Deprecation` header for one release.

### 1.3 Files changed

| File | Action |
|---|---|
| `laniakea/core/unified_system.py` | delete |
| `laniakea/__init__.py` | keep, verify imports |
| `laniakea/api/main.py` | remove inline fallback routes for `/knowledge_market/*` and `/scda/*` (routers own them now) |

### 1.4 Verification

```bash
source .venv/bin/activate
python -c "from laniakea.api.main import app; print(len(app.routes))"
# Expect: < 89 (fewer duplicates), no errors.
grep -rn "sys.path.insert" laniakea/
# Expect: no matches.
pytest tests/test_api_endpoints.py -q
# Expect: green.
```

### 1.5 Commit

```bash
git add -A
git commit -m "chore(hygiene): remove hardcoded path + dead unified_system module"
git push origin main
```

---

## Step 2 — Config unification

### 2.1 Problem

Two parallel config modules exist:

* `laniakea/core/config.py` — class-based, used by `api/main.py` and `utils/logger.py`.
* `laniakea/utils/config.py` — dataclass-based, used by 7 other modules.

They define overlapping fields (host, port, JWT secret, etc.) with
**slightly different defaults** (e.g. `API_PORT` is 8000 in one, 5000 in
the other). This is a footgun.

### 2.2 Plan

1. Convert `laniakea/core/config.py` to a `pydantic-settings` `BaseSettings`.
2. Add every field currently in `laniakea/utils/config.py` to it.
3. Make `laniakea/utils/config.py` a thin shim that imports
   `from laniakea.core.config import settings` and exposes
   `get_config()` returning a dict copy.
4. Add a deprecation warning on first use of the legacy `get_config()`.
5. Add a test that asserts both paths return equivalent data.

### 2.3 Files changed

| File | Action |
|---|---|
| `laniakea/core/config.py` | refactor to `pydantic_settings.BaseSettings` |
| `laniakea/utils/config.py` | become a shim |
| `tests/test_config.py` (new) | assert both paths work |

### 2.4 Verification

```bash
python -c "from laniakea.core.config import settings; print(settings.API_PORT, settings.TOTAL_TOKEN_SUPPLY)"
python -c "from laniakea.utils.config import get_config; print(get_config())"
pytest tests/test_config.py -q
```

### 2.5 Commit

```bash
git commit -m "refactor(config): unify on pydantic-settings, shim legacy imports"
git push origin main
```

---

## Step 3 — Live state persistence

### 3.1 Problem

`SCDA`, `DiplomacySystem`, `KnowledgeMarketplace`, and `AchievementSystem`
all live in process memory. On Render free tier, the dyno sleeps every
15 min of inactivity, and **every redeploy wipes the state**. A user who
spent an hour building a SCDA loses it.

### 3.2 Plan

1. Add `laniakea/storage/persistence.py` exposing a tiny
   `StateStore` class that saves pickled blobs to a SQLAlchemy table
   (`state_kv`).
2. Each subsystem gets a `save()` and `restore()` method that round-trips
   through the store. They are called on mutation + on boot.
3. A startup hook in `laniakea/api/main.py` orchestrates the rehydration
   order (deps first: nothing; then SCDA; then diplomacy; then market; then achievements).
4. A new `GET /core/persistence` endpoint reports last_save timestamps
   per subsystem for debugging.

### 3.3 Files changed

| File | Action |
|---|---|
| `laniakea/storage/persistence.py` (new) | `StateStore` class + `state_kv` table |
| `laniakea/intelligence/scda_manager.py` | `save()` + `restore()` |
| `laniakea/governance/metaverse_diplomacy.py` | `save()` + `restore()` |
| `laniakea/marketplace/knowledge_market.py` | `save()` + `restore()` |
| `laniakea/achievements/system.py` | `save()` + `restore()` |
| `laniakea/api/main.py` | startup hook + `/core/persistence` |
| `migrations/versions/0002_state_kv.py` (new) | alembic revision for the new table |

### 3.4 Verification

```bash
# Local
python -c "
from laniakea.intelligence.scda_manager import get_scda_manager
m = get_scda_manager(); m.create('test_001')
from laniakea.storage.persistence import StateStore
StateStore().save('scda', m)
"
# restart python
python -c "
from laniakea.storage.persistence import StateStore
from laniakea.intelligence.scda_manager import ScdaManager
m = ScdaManager(); m.restore(StateStore().load('scda'))
print('test_001' in m.list_identities())  # True
"
pytest tests/test_persistence.py -q
```

### 3.5 Commit

```bash
git commit -m "feat(persistence): rehydrate SCDA/diplomacy/knowledge/achievements from SQLAlchemy on boot"
git push origin main
```

---

## Step 4 — Observability v2

### 4.1 Problem

We have Prometheus exposition (`/observability/prometheus`) and a custom
counter (`/observability/requests`), but:

* No request-level tracing (only a request-id header).
* No latency histogram.
* No way to see *which* subsystem is slow under load.

### 4.2 Plan

1. Add `laniakea/observability/tracing.py` — `get_tracer()` returning
   an OpenTelemetry tracer. If `OTEL_EXPORTER_OTLP_ENDPOINT` is unset,
   the tracer is a no-op.
2. Wrap every request in the existing middleware stack with a span.
3. Add per-subsystem counters: `laniakea.scda.solve`,
   `laniakea.marketplace.buy`, `laniakea.diplomacy.create_alliance`,
   `laniakea.governance.vote`, etc.
4. Extend `/observability/snapshot` with `latency_p50`, `latency_p95`,
   `error_rate`, and the last 50 traces.

### 4.3 Files changed

| File | Action |
|---|---|
| `laniakea/observability/tracing.py` (new) | `get_tracer()` |
| `laniakea/observability/metrics.py` (new) | per-subsystem counters |
| `laniakea/api/middleware.py` | span wrapping |
| `laniakea/api/observability_api.py` | extend `/snapshot` |

### 4.4 Verification

```bash
curl -s http://localhost:8000/observability/snapshot | jq .
# Expect latency_p50, latency_p95, traces, counters.

OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317 python main.py start
# Expect OTel exporter to be initialised (check logs).
```

### 4.5 Commit

```bash
git commit -m "feat(observability): OpenTelemetry tracing + structured per-subsystem metrics"
git push origin main
```

---

## Step 5 — OpenAPI enrichment + auth-ready scaffolding

### 5.1 Problem

The auto-generated `/openapi.json` is technically valid but every route
has the same boilerplate `summary="A get endpoint"`. External integrators
can't tell what a route does without hitting it. Also, the most
sensitive POST routes (mine, train, vote) are public, which is a
deployment risk for white-label installs.

### 5.2 Plan

1. Add a `laniakea/api/openapi.py` helper that registers tag metadata
   (description, external docs URL).
2. Manually add `summary`/`description`/`responses` to every public
   decorator in `laniakea/api/main.py` (and routers).
3. Add `laniakea/security/deps.py` exposing `require_auth` (JWT bearer).
4. Gate the highest-blast-radius POSTs behind `Depends(require_auth)`,
   but only when env var `LANIAKEA_AUTH_ENABLED=true`. Default = off,
   so the public Render URL stays open.

### 5.3 Files changed

| File | Action |
|---|---|
| `laniakea/api/openapi.py` (new) | tag metadata |
| `laniakea/api/main.py` | per-route metadata + auth gate |
| `laniakea/security/deps.py` (new) | `require_auth` dependency |
| `laniakea/security/auth.py` | extend token issuance |

### 5.4 Verification

```bash
curl -s http://localhost:8000/openapi.json | jq '.paths."/blockchain/mine".post.summary'
# Expect: "Forge a new block (PoA signed)"
LANIAKEA_AUTH_ENABLED=true python main.py start
curl -i -X POST http://localhost:8000/blockchain/mine
# Expect: 401 Unauthorized
curl -i -X POST http://localhost:8000/blockchain/mine -H "Authorization: Bearer $TOKEN"
# Expect: 200 OK
```

### 5.5 Commit

```bash
git commit -m "feat(api): enrich OpenAPI surface + optional JWT auth gate"
git push origin main
```

---

## Step 6 — Test coverage + load-test profile

### 6.1 Problem

Existing tests are slim — they cover boot, a few AI helpers, and SCDA
math. Many subsystems (knowledge market, diplomacy, persistence,
observability) have no test at all. There's a `locustfile.py` but it
only hits blockchain and SCDA.

### 6.2 Plan

1. Add `tests/test_knowledge_market.py` — tokenize → list → buy → asset details.
2. Add `tests/test_diplomacy.py` — create alliance → reputation update → stats.
3. Add `tests/test_persistence.py` — save/restore round-trip.
4. Add `tests/test_observability.py` — snapshot shape after N requests.
5. Extend `tests/test_api_endpoints.py` to hit every route under `/`.
6. Extend `locustfile.py` with market + diplomacy flows.
7. Set `pytest.ini` with `--cov-fail-under=60`.

### 6.3 Files changed

| File | Action |
|---|---|
| `tests/test_knowledge_market.py` (new) | |
| `tests/test_diplomacy.py` (new) | |
| `tests/test_persistence.py` (new) | |
| `tests/test_observability.py` (new) | |
| `tests/test_api_endpoints.py` | extend |
| `locustfile.py` | extend |
| `pytest.ini` | coverage gate |

### 6.4 Verification

```bash
pytest --cov=laniakea --cov-report=term-missing
# Expect: 60% < TOTAL < 100% and all tests green.

locust -f locustfile.py --headless -u 10 -r 2 -t 30s --host https://laniakea-protocol.onrender.com
# Expect: 0 failures, p95 < 2s on the static endpoints.
```

### 6.5 Commit

```bash
git commit -m "test(coverage): bring api+intelligence+marketplace+governance to ≥60%"
git push origin main
```

---

## Cross-cutting conventions (every step)

* **Style:** match existing code (PEP 8 + Black default 88).
* **Logging:** use the shared `laniakea.utils.logger.setup_logger` — no
  `print()` for state changes.
* **Imports:** order = stdlib, third-party, `laniakea.*`. Use the shim
  `from laniakea.core.config import settings` everywhere.
* **Errors:** raise `laniakea.core.exceptions.LaniakeaError` subclasses,
  not raw `Exception`.
* **Authorship:** add `__author__ = "LaniakeA Dev"` only on new top-level
  files; sub-modules inherit.

---

**Status legend**

* 🟢 done
* 🟡 in progress
* ⚪ not started

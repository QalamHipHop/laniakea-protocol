# LaniakeA Protocol — Developer Guide

**Author:** LaniakeA Dev

## Local Setup

```bash
git clone https://github.com/QalamHipHop/laniakea-protocol.git
cd laniakea-protocol
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

## Running

```bash
# API server
python main.py
# or with uvicorn directly
uvicorn laniakea.api.main:app --host 0.0.0.0 --port 8000 --reload
```

Open http://localhost:8000/docs for the interactive Swagger UI.

## Running Tests

```bash
pytest -q
# Quick smoke test
python smoke_test.py
# Fastest path
python test_quick.py
```

## Project Layout

```
laniakea/                  # main package
  api/                     # FastAPI routes
  core/                    # blockchain, SCDA, wallet
  blockchain/              # mining, core
  consensus/               # PoV / PoA / PoHD
  crosschain/              # bridge
  defi/                    # swap
  governance/              # DAO + diplomacy
  ai/                      # LLM + problem discovery
  evolution/               # SCDA evolution
  knowledge/               # knowledge market
  websocket/               # WebSocket manager
  storage/                 # database
  utils/                   # logger, config
web/                       # static UI (HTML/JS)
main.py                    # unified entry point
tests/                     # pytest suite
docs/                      # documentation
```

## Coding Conventions

- Python ≥ 3.11
- Type hints everywhere
- `black` + `flake8` + `mypy` (configured in `pyproject.toml`)
- Heavy optional deps (`openai`, `psycopg2`, `web3`) imported lazily

## Adding a New API Endpoint

1. Add the handler in `laniakea/api/main.py` (or a new router under
   `laniakea/api/`) and register it on the `app` instance.
2. If it talks to the chain, use the `HypercubeBlockchain` singleton from
   `laniakea.core.hypercube_blockchain`.
3. Add a smoke test under `tests/`.
4. Update `docs/ARCHITECTURE.md` if it introduces a new domain.

## Adding a New Module

1. Create `laniakea/<area>/__init__.py` + your module file.
2. If it is imported by `laniakea.api.main`, prefer **lazy imports** to
   keep cold-start fast.
3. Wire config via `laniakea.core.config` (env-var backed).

## Releasing

- Bump `VERSION`.
- Update `CHANGELOG.md`.
- Tag: `git tag v3.x.y && git push --tags`.
- Render.com auto-deploys on `main` push.

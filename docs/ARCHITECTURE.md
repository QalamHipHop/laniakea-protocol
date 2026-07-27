# LaniakeA Protocol — Architecture

**Version:** 3.0.0 (v0.0.01) · **Maintainer:** LaniakeA Dev

## Overview

LaniakeA is an 8-dimensional blockchain superprotocol implementing SCDA
(Single-Cell Digital Account) evolution, knowledge markets, and metaverse
diplomacy on top of a hypercube-structured ledger.

## Layered Architecture

```
┌──────────────────────────────────────────────────────┐
│  L5  · Application    : web/ (dashboards, metaverse) │
├──────────────────────────────────────────────────────┤
│  L4  · API Gateway    : laniakea/api/main.py         │
├──────────────────────────────────────────────────────┤
│  L3  · Domain         : blockchain · defi · dao ·    │
│                         governance · knowledge · ai   │
├──────────────────────────────────────────────────────┤
│  L2  · Consensus      : pov · poa · pohd             │
├──────────────────────────────────────────────────────┤
│  L1  · Core           : hypercube_blockchain ·       │
│                         scda · wallet · smart_contract│
├──────────────────────────────────────────────────────┤
│  L0  · Infra          : storage · network ·          │
│                         crosschain · monitoring       │
└──────────────────────────────────────────────────────┘
```

## Module Map (`laniakea/`)

| Package | Purpose |
|---|---|
| `core/` | Hypercube blockchain, SCDA, wallet, smart contract VM, standards |
| `blockchain/` | Core chain + mining system |
| `consensus/` | PoV, PoA, PoHD |
| `crosschain/` | Bridge + cross-chain manager |
| `defi/` | Swap / liquidity pools |
| `governance/` | DAO + metaverse diplomacy |
| `ai/` | LLM integration, problem discovery, evaluator |
| `evolution/` | SCDA evolution managers |
| `knowledge/` | Knowledge market, assets, vector engine |
| `intelligence/` | SCDA model, cosmic brain |
| `api/` | FastAPI routes, WebSocket gateway, scientific API |
| `websocket/` | WebSocket manager + realtime updates |
| `storage/` | Database, models, setup, extensions |
| `network/` | Legacy network façade |
| `cli/` | CLI entry points |
| `dashboard/` | Live + advanced dashboards, metrics |
| `identity/` | DID system |
| `achievements/` | Achievement system |
| `analytics/` | Telemetry |
| `security/` | Auth (OAuth2 / JWT) |
| `external_apis/` | External integrations |
| `utils/` | Logger, config |

## Key Design Decisions

1. **Hypercube ledger (8D)** — every block carries 8-dimensional coordinates;
   consensus is reached via Proof-of-Human-Development (PoHD) where the
   "distance" from a hypercube anchor is the difficulty metric.
2. **SCDA as the unit of intelligence** — every participant starts at
   `C(0)=1.0` and evolves via diminishing returns:
   `ΔC = D(P) / C(t)^α`, with `α = 1.5`.
3. **Knowledge market** — solved problems become tradable KnowledgeAssets
   with reputation-weighted pricing.
4. **Diplomacy first-class** — alliances, treaties, and relations are
   persisted in the same store as the ledger, not in a side-channel.
5. **Optional heavy deps** — `openai`, `web3`, `psycopg2` are imported
   lazily so the service still boots on minimal environments.

## Live Topology

- **Service ID:** `srv-d4683hali9vc73dc6c4g`
- **URL:** https://laniakea-protocol.onrender.com
- **CI:** GitHub Actions (`.github/workflows/`)
- **Observability:** Prometheus + Grafana (`monitoring/`), Nginx (`nginx/`)

## Further Reading

- Whitepaper — `docs/WHITEPAPER.md`
- API reference — `docs/api/`
- Deployment — `docs/deployment/`
- Developer guide — `docs/DEVELOPER_GUIDE.md`
- Security policy — `docs/SECURITY.md`

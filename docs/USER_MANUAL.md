# LaniakeA Protocol — User Manual

**Version:** 3.0.0 (v0.0.01) · **Author:** LaniakeA Dev

## What is LaniakeA?

LaniakeA is a cosmic-scale blockchain where every participant is a
**Single-Cell Digital Account (SCDA)** that grows in complexity by solving
*Hard Problems* generated and validated by an integrated LLM.

## First Steps

1. Visit https://laniakea-protocol.onrender.com
2. Open `/docs` to browse the interactive API.
3. Get your SCDA via `GET /scda/{user_id}/state`.
4. Solve a problem: `POST /ai/query` or `POST /blockchain/mine`.
5. Watch your complexity `C(t)` grow and your tier upgrade.

## Key Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness probe |
| GET | `/discovery` | Service self-description |
| GET | `/core/status` | Runtime status |
| GET | `/blockchain/info` | Chain info |
| GET | `/blockchain/chain` | Full chain (paginated) |
| POST | `/blockchain/mine` | Mine a new block |
| GET | `/token/info` | Token economics |
| GET | `/defi/pools` | Liquidity pools |
| GET | `/governance/proposals` | DAO proposals |
| GET | `/diplomacy/alliances` | Active alliances |
| GET | `/achievements/catalog` | All achievements |
| WS | `/ws/{type}/{id}` | Realtime channel |

## Dashboards

The `web/` directory ships with:

- `index.html` — landing page
- `dashboard.html` — operational dashboard
- `metaverse_8d_visualization.html` — 8D hypercube viewer
- `mining_dashboard.html` — mining status
- `scda_dashboard.html` — SCDA evolution tracker
- `social_hub.html` — diplomacy hub
- `achievements.html` — achievement gallery
- `3d-visualization.html` — 3D block space

## Support

- GitHub Issues: https://github.com/QalamHipHop/laniakea-protocol/issues
- Security: see `docs/SECURITY.md`

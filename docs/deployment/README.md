# Deployment

The LaniakeA Protocol is designed to deploy with a single command on
Render.com (see `render.yaml`) or via Docker (`Dockerfile` +
`docker-compose.yml`).

## Production

- **Service ID:** `srv-d4683hali9vc73dc6c4g`
- **URL:** https://laniakea-protocol.onrender.com
- **Trigger:** push to `main` on GitHub → auto-deploy

## Required environment variables

| Var | Purpose |
|---|---|
| `LANIAKEA_WALLET_ENCRYPTION_KEY` | Wallet encryption key (see `docs/SECURITY.md`) |
| `API_HOST` | Bind host (default `0.0.0.0`) |
| `API_PORT` / `PORT` | Bind port (Render injects `PORT`) |
| `MINING_DIFFICULTY` | PoW difficulty |
| `AUTHORITIES` | Comma-separated validator list |
| `SUPPORTED_CHAINS` | Comma-separated cross-chain allow-list |
| `MAX_QUBITS` | Quantum simulator cap |
| `LOG_LEVEL` | `info` / `debug` / `warning` |

See `.env.example` for the full set.

## Local container

```bash
docker compose up --build
```

## Reverse proxy

A starter Nginx config lives in `nginx/`. Use it as a template for
production TLS termination.

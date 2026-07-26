# 📡 Laniakea API Reference

Complete REST API documentation. The OpenAPI 3.0 spec lives in [`openapi.yaml`](./openapi.yaml).

## 🚀 Quick Start

```bash
# Base URL
https://laniakea-protocol.onrender.com

# Local
http://localhost:8000
```

## 🔑 Authentication

Most read endpoints are public. Write endpoints require JWT bearer token:

```bash
curl -H "Authorization: Bearer $TOKEN" https://laniakea-protocol.onrender.com/api/v1/scda
```

## 📚 Interactive Docs

- **Swagger UI:** `/docs`
- **ReDoc:** `/redoc`
- **OpenAPI JSON:** `/openapi.json`

## 🔌 WebSocket

Real-time updates at `wss://laniakea-protocol.onrender.com/ws`.

```javascript
const ws = new WebSocket('wss://laniakea-protocol.onrender.com/ws');
ws.onmessage = (e) => {
  const msg = JSON.parse(e.data);
  // msg.type: 'block' | 'scda' | 'metric' | 'problem' | 'governance'
  console.log(msg);
};
```

## 📋 Endpoint Groups

| Group | Base | Description |
|---|---|---|
| System | `/health`, `/metrics` | Health, Prometheus |
| SCDA | `/api/v1/scda` | Account CRUD, evolve, breed |
| Blockchain | `/api/v1/blockchain` | Blocks, transactions |
| Problems | `/api/v1/problems` | Hard Problems |
| Governance | `/api/v1/governance` | DAO proposals, voting |
| Metaverse | `/api/v1/metaverse` | 8D space |

## 🧬 SCDA Lifecycle

```bash
# 1. Create
curl -X POST .../api/v1/scda -d '{"owner":"0x..."}'

# 2. Evolve
curl -X POST .../api/v1/scda/{id}/evolve

# 3. Breed
curl -X POST .../api/v1/scda/{id}/breed -d '{"partner_id":"..."}'

# 4. List
curl .../api/v1/scda?tier=T3
```

## 🔄 Rate Limits

- 100 req/min per IP for public endpoints
- 1000 req/min for authenticated users
- WebSocket: 10 messages/sec

## 🌐 SDKs (planned)

- Python: `pip install laniakea-sdk`
- JavaScript: `npm install @laniakea/sdk`
- Rust: `cargo add laniakea-sdk`

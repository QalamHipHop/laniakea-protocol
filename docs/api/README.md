# API Examples

Sample requests and responses for the most-used endpoints of the
LaniakeA Protocol.

The full schema is always available at:

- **Live:** https://laniakea-protocol.onrender.com/docs
- **Local:** http://localhost:8000/docs

## Quick Examples

### Health

```bash
curl https://laniakea-protocol.onrender.com/health
```

### Chain Info

```bash
curl https://laniakea-protocol.onrender.com/blockchain/info
```

### Token Economics

```bash
curl https://laniakea-protocol.onrender.com/token/info
```

### Submit an AI Query

```bash
curl -X POST https://laniakea-protocol.onrender.com/ai/query \
  -H 'Content-Type: application/json' \
  -d '{"prompt": "What is the SCDA evolution law?"}'
```

### WebSocket

```javascript
const ws = new WebSocket("wss://laniakea-protocol.onrender.com/ws/public/live");
ws.onmessage = (e) => console.log(JSON.parse(e.data));
```

See `docs/ARCHITECTURE.md` for the layered model behind these routes.

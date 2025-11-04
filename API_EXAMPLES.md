# API Examples - Laniakea Protocol v0.0.1

## Live Server

**URL**: https://8000-inpdc32l9bq3e8cbcd5zh-09b986b7.manus.computer

---

## Example Responses

### 1. Node Information

**Request:**
```bash
curl https://8000-inpdc32l9bq3e8cbcd5zh-09b986b7.manus.computer/
```

**Response:**
```json
{
  "node_id": "c90c27ff25817870c332578baafb84e00a91ec2a3896d0d1242c968f9b621543",
  "host": "0.0.0.0",
  "p2p_port": 5000,
  "api_port": 8000,
  "specialties": ["solving", "mining", "ai_inference"],
  "reputation": 0.0,
  "total_value_created": {
    "knowledge": 0.0,
    "computation": 0.0,
    "originality": 0.0,
    "consciousness": 0.0,
    "environmental": 0.0,
    "health": 0.0
  }
}
```

---

### 2. Blockchain Statistics

**Request:**
```bash
curl https://8000-inpdc32l9bq3e8cbcd5zh-09b986b7.manus.computer/stats
```

**Response:**
```json
{
  "blockchain": {
    "length": 2,
    "total_transactions": 1,
    "total_solutions": 0,
    "total_value_created": {
      "knowledge": 0.0,
      "computation": 0.0,
      "originality": 0.0,
      "consciousness": 0.0,
      "environmental": 0.0,
      "health": 0.0
    },
    "current_difficulty": 1.02,
    "unique_participants": 1
  },
  "network": {
    "connected_peers": 0,
    "total_messages": 0,
    "uptime_seconds": 120.5
  }
}
```

---

### 3. Dashboard (HTML)

**URL**: https://8000-inpdc32l9bq3e8cbcd5zh-09b986b7.manus.computer/dashboard

**Features:**
- Real-time blockchain metrics
- Beautiful gradient UI
- Responsive design
- Auto-refresh every 5 seconds

---

### 4. Create Task

**Request:**
```bash
curl -X POST https://8000-inpdc32l9bq3e8cbcd5zh-09b986b7.manus.computer/tasks/create \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Climate Change Prediction",
    "description": "Develop ML model for climate forecasting",
    "category": "scientific",
    "difficulty": 8.0
  }'
```

**Response:**
```json
{
  "task_id": "task_abc123...",
  "status": "created",
  "reward_estimate": {
    "knowledge": 80.0,
    "computation": 60.0,
    "originality": 70.0
  }
}
```

---

### 5. NFT Marketplace

**Request:**
```bash
curl https://8000-inpdc32l9bq3e8cbcd5zh-09b986b7.manus.computer/nft/marketplace
```

**Response:**
```json
{
  "total_nfts": 0,
  "active_listings": 0,
  "total_volume": 0.0,
  "trending": []
}
```

---

### 6. Predictive Analytics

**Request:**
```bash
curl https://8000-inpdc32l9bq3e8cbcd5zh-09b986b7.manus.computer/analytics/predict
```

**Response:**
```json
{
  "predictions": {
    "chain_length": {
      "next_hour": 3,
      "next_day": 26,
      "confidence": 0.95
    },
    "network_growth": {
      "trend": "stable",
      "forecast": "positive"
    }
  },
  "patterns_detected": ["steady_growth"],
  "risks": []
}
```

---

### 7. Cosmic Simulation

**Request:**
```bash
curl https://8000-inpdc32l9bq3e8cbcd5zh-09b986b7.manus.computer/simulation/status
```

**Response:**
```json
{
  "time": 10.0,
  "alive_cells": 1,
  "total_knowledge": 2.95,
  "max_generation": 0,
  "environment": {
    "temperature": 0.5,
    "knowledge_density": 0.029,
    "energy_field": 1.0
  }
}
```

---

## Testing the API

### Using cURL

```bash
# Get all tasks
curl https://8000-inpdc32l9bq3e8cbcd5zh-09b986b7.manus.computer/tasks

# View dashboard
curl https://8000-inpdc32l9bq3e8cbcd5zh-09b986b7.manus.computer/dashboard

# Get blockchain data
curl https://8000-inpdc32l9bq3e8cbcd5zh-09b986b7.manus.computer/blockchain
```

### Using Python

```python
import requests

BASE_URL = "https://8000-inpdc32l9bq3e8cbcd5zh-09b986b7.manus.computer"

# Get node info
response = requests.get(f"{BASE_URL}/")
print(response.json())

# Create task
task_data = {
    "title": "New Discovery",
    "description": "Breakthrough in quantum computing",
    "category": "scientific",
    "difficulty": 9.0
}
response = requests.post(f"{BASE_URL}/tasks/create", json=task_data)
print(response.json())
```

### Using JavaScript

```javascript
const BASE_URL = "https://8000-inpdc32l9bq3e8cbcd5zh-09b986b7.manus.computer";

// Get stats
fetch(`${BASE_URL}/stats`)
  .then(res => res.json())
  .then(data => console.log(data));

// Create task
fetch(`${BASE_URL}/tasks/create`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    title: "AI Research",
    description: "Novel neural architecture",
    category: "scientific",
    difficulty: 8.5
  })
})
  .then(res => res.json())
  .then(data => console.log(data));
```

---

**💫 Happy exploring the Laniakea Protocol!**

# 🚀 Laniakea Protocol - API Documentation

## 🌟 **Enhanced Blockchain Protocol API**

The Laniakea Protocol provides a comprehensive RESTful API with advanced AI, security, and real-time capabilities.

---

## 🔐 **Security & Authentication**

### **Security Status**
All endpoints are protected by our **Neural Security System** with:
- Real-time threat detection
- AI-powered pattern analysis
- Multi-layered verification
- Confidence scoring

### **Response Format (Blocked Requests)**
```json
{
  "error": "Request blocked",
  "reason": "Security system error", 
  "confidence": 1.0
}
```

---

## 🌐 **API Endpoints**

### **System Status Endpoints**

#### `GET /api/health`
**Purpose:** Basic health check
**Response:** System health status
**Security:** Standard monitoring

#### `GET /api/v1/status`
**Purpose:** Comprehensive system status
**Response:** 
```json
{
  "node_id": "laniakea-node-001",
  "enhanced_mode": true,
  "systems": {
    "security": "operational",
    "ai": "learning",
    "blockchain": "syncing",
    "optimization": "active"
  },
  "uptime": "auto",
  "performance": "optimized"
}
```

#### `GET /api/v1/metrics`
**Purpose:** Performance metrics
**Response:** Real-time system performance data

---

## 🔗 **Blockchain Endpoints**

### **Core Blockchain Operations**

#### `GET /api/v1/blockchain/info`
**Response:**
```json
{
  "chain_id": "laniakea-mainnet",
  "block_height": "current",
  "consensus": "enhanced",
  "difficulty": "adaptive",
  "node_count": "network_size"
}
```

#### `GET /api/v1/block/{height}`
**Purpose:** Get block by height
**Parameters:**
- `height` (path): Block height

#### `GET /api/v1/transaction/{hash}`
**Purpose:** Get transaction details
**Parameters:**
- `hash` (path): Transaction hash

---

## 🧠 **AI & Intelligence Endpoints**

### **Autonomous AI System**

#### `GET /api/v1/ai/status`
**Response:**
```json
{
  "autonomous_ai": "operational",
  "cosmic_brain": "processing",
  "knowledge_graph": "learning",
  "llm_client": "connected",
  "goals": ["system_optimization", "security_enhancement"],
  "performance_metrics": "auto_collected"
}
```

#### `POST /api/v1/ai/analyze`
**Purpose:** AI-powered analysis
**Body:** JSON data for analysis
**Response:** AI insights and recommendations

#### `GET /api/v1/ai/knowledge/graph`
**Purpose:** Access knowledge graph data
**Response:** Knowledge graph structure and insights

---

## ⚡ **Performance & Optimization**

### **Performance Optimizer**

#### `GET /api/v1/optimization/status`
**Response:**
```json
{
  "strategy": "BALANCED",
  "auto_optimization": true,
  "performance_metrics": {
    "cpu_usage": "optimized",
    "memory_efficiency": "high",
    "quantum_optimization": "enabled"
  },
  "recommendations": "auto_generated"
}
```

#### `POST /api/v1/optimization/tune`
**Purpose:** Manual performance tuning
**Body:** Optimization parameters

---

## 🛡️ **Security Endpoints**

### **Enhanced Security**

#### `GET /api/v1/security/status`
**Response:**
```json
{
  "security_level": "HIGH",
  "neural_security": "active",
  "threat_detection": "realtime",
  "encryption_status": "military_grade",
  "protection_confidence": 1.0
}
```

#### `GET /api/v1/security/threats`
**Purpose:** Current threat analysis
**Response:** Real-time threat intelligence

---

## 🌐 **WebSocket & Real-time**

### **Real-time Updates**

#### `WebSocket /ws/updates`
**Purpose:** Real-time system updates
**Events:**
- Block additions
- Transaction confirmations
- Security alerts
- Performance metrics
- AI insights

#### `WebSocket /ws/notifications`
**Purpose:** Event-driven notifications
**Events:**
- System alerts
- Optimization recommendations
- Security warnings
- AI discoveries

---

## 📊 **Monitoring & Analytics**

### **System Monitoring**

#### `GET /api/v1/monitor/metrics`
**Response:** Real-time performance metrics
**Includes:**
- CPU and memory usage
- Network performance
- Blockchain metrics
- AI system performance

#### `GET /api/v1/monitor/logs`
**Purpose:** System logs and events
**Parameters:**
- `level` (query): Log level
- `since` (query): Timestamp filter

---

## 🔧 **Configuration & Management**

### **System Configuration**

#### `GET /api/v1/config`
**Purpose:** Current system configuration
**Response:** System settings and parameters

#### `PUT /api/v1/config`
**Purpose:** Update configuration
**Body:** Configuration updates
**Security:** Admin access required

---

## 🌌 **Advanced Features**

### **Cosmic Brain AI**

#### `GET /api/v1/cosmic/analysis`
**Purpose:** Multi-dimensional analysis
**Response:** Cosmic-level insights and patterns

#### `POST /api/v1/cosmic/optimize`
**Purpose:** Quantum-inspired optimization
**Body:** Optimization request parameters

### **Knowledge Graph**

#### `GET /api/v1/knowledge/nodes`
**Purpose:** Access knowledge nodes
**Response:** Knowledge graph structure

#### `POST /api/v1/knowledge/learn`
**Purpose:** Add knowledge to graph
**Body:** Knowledge data

---

## 📈 **Response Standards**

### **Success Response Format**
```json
{
  "status": "success",
  "data": {...},
  "timestamp": "ISO_8601",
  "node_id": "laniakea-node-001",
  "enhanced_features": true
}
```

### **Error Response Format**
```json
{
  "status": "error", 
  "error": "error_type",
  "message": "description",
  "timestamp": "ISO_8601",
  "security_info": {...}
}
```

---

## 🚀 **Usage Examples**

### **Basic Health Check**
```bash
curl http://localhost:8000/api/health
```

### **System Status**
```bash
curl http://localhost:8000/api/v1/status
```

### **AI Analysis**
```bash
curl -X POST http://localhost:8000/api/v1/ai/analyze \
  -H "Content-Type: application/json" \
  -d '{"data": "sample_data"}'
```

### **WebSocket Connection**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/updates');
ws.onmessage = function(event) {
  console.log('Update:', JSON.parse(event.data));
};
```

---

## 🛡️ **Security Notes**

1. **All requests are monitored** by the Neural Security System
2. **Rate limiting** is automatically applied
3. **Threat assessment** is performed in real-time
4. **Suspicious activity** triggers immediate response
5. **API keys and credentials** are managed securely

---

## 🌟 **Enhanced Features**

- **AI-powered responses** with intelligent insights
- **Real-time optimization** suggestions
- **Multi-dimensional analysis** capabilities
- **Quantum-inspired algorithms** for performance
- **Neural security protection** on all endpoints
- **Cosmic pattern recognition** for advanced analytics

---

*API Documentation v1.0*  
*Enhanced with Cosmic Brain AI Integration*  
*Last Updated: 2025-11-06*
---

## 💎 **Knowledge Market Endpoints**

### **Operational Knowledge Market (NFT-Inspired)**

#### `GET /market/token`
**Purpose:** Get information about the Knowledge Market's fungible token (KNOW).
**Response:** Token details (ID, symbol, name, total supply).

#### `POST /market/assets`
**Purpose:** Mint a new Knowledge Asset (NFT).
**Request Body:**
```json
{
  "owner_id": "string",
  "title": "string",
  "description": "string",
  "content_hash": "string",
  "metadata_uri": "string"
}
```
**Response:** Details of the newly minted asset.

#### `GET /market/assets`
**Purpose:** Get a list of all minted Knowledge Assets.

#### `PUT /market/assets/{asset_id}/list`
**Purpose:** List a Knowledge Asset for sale.
**Parameters:**
- `asset_id` (path): ID of the asset.
- `price` (query): Price in KNOW or LANA.

#### `POST /market/assets/{asset_id}/purchase`
**Purpose:** Purchase a Knowledge Asset.
**Parameters:**
- `asset_id` (path): ID of the asset.
- `buyer_id` (query): ID of the purchasing entity.

---

## 🏛️ **Diplomacy Endpoints**

### **Inter-SCDA Diplomacy System**

#### `PUT /diplomacy/relation/{id1}/{id2}`
**Purpose:** Update the diplomatic status between two entities.
**Parameters:**
- `id1` (path): First entity ID.
- `id2` (path): Second entity ID.
**Request Body:**
```json
{
  "status": "Alliance" | "Hostile" | "Neutral" | "War" | "Peace"
}
```
**Response:** Updated relation details.

#### `GET /diplomacy/relation/{id1}/{id2}`
**Purpose:** Get the diplomatic relation between two entities.

#### `POST /diplomacy/treaties`
**Purpose:** Create a new treaty.
**Request Body:**
```json
{
  "parties": ["string", "string"],
  "treaty_type": "Trade" | "Defense" | "Research" | "Non-Aggression",
  "start_date": "datetime",
  "end_date": "datetime" | null,
  "terms": "string"
}
```
**Response:** Details of the newly created treaty.

#### `PUT /diplomacy/treaties/{treaty_id}/end`
**Purpose:** End an existing treaty.
**Parameters:**
- `treaty_id` (path): ID of the treaty.

---

## 🧠 **LLM Integration Endpoints**

### **Hard Problem Generation and Validation**

#### `POST /llm/generate-hard-problem`
**Purpose:** Generate a new 'Hard Problem' for PoHD using the LLM.
**Request Body:**
```json
{
  "context": "Current state of SCDA evolution or blockchain data."
}
```
**Response:** The generated Hard Problem equation/statement.

#### `POST /llm/validate-hard-problem`
**Purpose:** Validate a proposed solution to a 'Hard Problem' using the LLM.
**Request Body:**
```json
{
  "problem": "The Hard Problem statement",
  "proposed_solution": "The proposed solution"
}
```
**Response:** Validation status (`is_valid`: boolean) and explanation.

# 🌌 LaniakeA Protocol

**8-Dimensional Blockchain with AI Intelligence**

[![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)](https://github.com/QalamHipHop/laniakea-protocol)
[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-success.svg)](https://laniakea-protocol.onrender.com)

## 🚀 Overview

LaniakeA Protocol is a revolutionary blockchain system that implements an **8-dimensional hypercube architecture** based on advanced mathematical principles. It combines quantum-resistant cryptography, artificial intelligence, and cosmic consciousness for next-generation decentralized applications.

### ✨ Key Features

- **🎲 8-Dimensional Blockchain**: Hypercube-based block structure with spatial coordinates
- **🧠 AI-Powered Intelligence**: Cosmic Brain AI for autonomous optimization
- **🔐 Quantum-Resistant**: Advanced cryptography for future-proof security
- **⚡ High Performance**: Optimized consensus mechanism (Proof of HyperDistance)
- **🌐 Cross-Chain**: Multi-chain interoperability support
- **🔄 Self-Evolving**: Autonomous learning and adaptation
- **📊 Real-Time Analytics**: Live dashboards and monitoring
- **🛡️ Enterprise-Grade**: Production-ready with comprehensive testing

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## 🔧 Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git

### Clone Repository

```bash
git clone https://github.com/QalamHipHop/laniakea-protocol.git
cd laniakea-protocol
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Environment Setup

Create a `.env` file:

```env
NODE_ID=laniakea-node-001
ENVIRONMENT=production
LOG_LEVEL=INFO
JWT_SECRET=your-secret-key
ENCRYPTION_KEY=your-encryption-key
```

## 🚀 Quick Start

### Start the Node

```bash
python main.py start --host 0.0.0.0 --port 8000
```

### Check Status

```bash
python main.py status
```

### Create Transaction

```bash
curl -X POST http://localhost:8000/api/v1/transaction \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "alice",
    "recipient": "bob",
    "amount": 100
  }'
```

### Mine Block

```bash
curl -X POST http://localhost:8000/api/v1/mine?miner_address=miner1
```

## 🏗️ Architecture

### 8-Dimensional Hypercube

LaniakeA implements a unique 8-dimensional blockchain architecture:

```
Dimensions:
1. Time (t)
2. Space X (x)
3. Space Y (y)
4. Space Z (z)
5. Energy (e)
6. Quantum State (q)
7. Information Density (i)
8. Consciousness Level (c)
```

Each block exists in 8D space with coordinates `[t, x, y, z, e, q, i, c]`.

### Consensus Mechanism

**Proof of HyperDistance (PoHD)**

- Blocks are validated based on their Euclidean distance from the hypercube center
- Lower distance = higher validity
- Difficulty adjusts dynamically based on network conditions

### Core Components

```
laniakea/
├── core/
│   ├── hypercube_blockchain.py  # 8D blockchain implementation
│   └── blockchain.py             # Legacy blockchain (deprecated)
├── intelligence/
│   └── brain.py                  # Cosmic Brain AI
├── network/
│   └── api.py                    # FastAPI REST interface
├── utils/
│   ├── logger.py                 # Advanced logging system
│   └── config.py                 # Configuration management
└── cli/
    └── commands.py               # Command-line interface
```

## 📚 API Documentation

### Endpoints

#### Health Check

```http
GET /health
```

Returns server health status.

#### Get Blockchain Status

```http
GET /api/v1/status
```

Returns comprehensive blockchain statistics.

#### Get Full Blockchain

```http
GET /api/v1/blockchain
```

Returns complete blockchain data.

#### Create Transaction

```http
POST /api/v1/transaction
Content-Type: application/json

{
  "sender": "string",
  "recipient": "string",
  "amount": number,
  "metadata": {}
}
```

#### Mine Block

```http
POST /api/v1/mine?miner_address=string
```

#### Get Balance

```http
GET /api/v1/balance/{address}
```

## 💻 Development

### Run in Development Mode

```bash
python main.py start --dev --reload
```

### Run Tests

```bash
pytest tests/
```

### Code Style

```bash
black laniakea/
flake8 laniakea/
```

## 🌐 Deployment

### Render Deployment

The project is configured for automatic deployment on Render:

1. Connect your GitHub repository to Render
2. Use the `render.yaml` configuration
3. Set environment variables in Render dashboard
4. Deploy automatically on push to main branch

**Live URL**: https://laniakea-protocol.onrender.com

### Docker Deployment

```bash
docker build -t laniakea-protocol .
docker run -p 8000:8000 laniakea-protocol
```

### Environment Variables

Required environment variables for production:

- `PORT`: Server port (default: 8000)
- `NODE_ID`: Unique node identifier
- `ENVIRONMENT`: production/development
- `JWT_SECRET`: Secret key for JWT tokens
- `ENCRYPTION_KEY`: Encryption key for sensitive data
- `LOG_LEVEL`: Logging level (INFO/DEBUG/WARNING/ERROR)

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](docs/guides/CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Acknowledgments

- Inspired by cosmic structures and mathematical beauty
- Built with passion for decentralized future
- Powered by the LaniakeA community

## 📞 Contact

- **Website**: https://laniakea-protocol.onrender.com
- **GitHub**: https://github.com/QalamHipHop/laniakea-protocol
- **Issues**: https://github.com/QalamHipHop/laniakea-protocol/issues

---

**Made with ❤️ by the LaniakeA Team**

*Exploring the universe, one block at a time* 🌌

# LaniakeA Protocol: The Cosmic Evolution Engine

<div align="center">

![Version](https://img.shields.io/badge/Version-1.0.0--Unified-7c3aed?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11.9-3776ab?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-fbbf24?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Live_Production-10b981?style=for-the-badge)
![Uptime](https://img.shields.io/badge/Uptime-99.9%25-06b6d4?style=for-the-badge)

### 🌌 *"The Cosmic Evolution Engine"*

**یک ابرپروتکل محاسباتی کیهانی برای تکامل هوش جمعی**

**[🚀 Live Demo](https://laniakea-protocol.onrender.com)** · **[📚 Docs](https://laniakea-protocol.onrender.com/docs)** · **[🔬 Whitepaper](./docs/WHITEPAPER.md)** · **[🏗️ Architecture](./docs/ARCHITECTURE.md)**

</div>

---

## 🎯 چشم‌انداز

**LaniakeA Protocol** یک سیستم محاسباتی کیهانی است که با الهام از ساختار جهان هستی، یک اکوسیستم غیرمتمرکز برای **تکامل هوش جمعی** ایجاد می‌کند. این پروتکل بر پایه‌ی مفاهیم زیر استوار است:

| # | مفهوم | توضیح |
|---|-------|-------|
| 🧬 | **تکامل هوش** | شبیه‌سازی تکامل از سلول تک‌یاخته تا هوش کیهانی از طریق **SCDA (Single-Cell Digital Account)** |
| 🔷 | **بلاکچین ۸D** | اولین بلاکچین هایپرکیوب هشت‌بعدی جهان با مکانیسم اجماع **PoHD (Proof of Human Development)** |
| 🧠 | **هوش مصنوعی** | یکپارچه‌سازی LLM برای تولید و اعتبارسنجی **Hard Problems** (معادلات بلوک‌سازی) |
| 🌐 | **متاورس** | فضای ۸ بعدی **دانش-آگاهی** با بصری‌سازی سه‌بعدی کامل (256 رأس، 1024 یال) |
| 💎 | **اقتصاد دانش** | PoHD به‌عنوان مکانیسم خلق ارزش + بازار دانش عملیاتی + NFT |
| 🏛️ | **تمدن‌سازی** | ساخت تمدن‌های دیجیتال + سیستم دیپلماسی و پیمان‌های بین‌تمدنی |
| 🔐 | **امنیت** | سیستم ایمنی عصبی ۵-حالته + MFA + JWT + rate-limiter + audit log رمزنگاری‌شده |
| 🌐 | **شبکه P2P** | DHT Kademlia + WebSocket transport برای شبکه غیرمتمرکز |

---

## ✨ ویژگی‌های کلیدی

### ۱. SCDA (Single-Cell Digital Account) — سه پیاده‌سازی

| ماژول | استفاده | ردیف |
|------|------|------|
| `laniakea.intelligence.scda_model` | **پیاده‌سازی اصلی** — DNA دیجیتال + Tier + breeding | اصلی |
| `laniakea.intelligence.scda_8d_vector` | بردار ۸ بعدی S(t) = (K(t), E(t)) — سازگار با whitepaper | علمی |
| `laniakea.intelligence.scda_legacy_compat` | سازگار با فرمول README — `α=1.5`، `k1=10`، `k2=50` | legacy |

**ثابت‌های SCDA:**
*   `EVOLUTIONARY_RESISTANCE_COEFFICIENT (α):` `1.5`
*   `INITIAL_COMPLEXITY (C(0)):` `1.0`
*   `INITIAL_ENERGY (E(0)):` `100.0`
*   `ENERGY_CONSUMPTION_FACTOR (k₁):` `10.0`
*   `ENERGY_REPLENISHMENT_FACTOR (k₂):` `50.0`

**قانون تکامل (PoHD):**
$$\Delta C = \frac{D(P)}{C(t)^\alpha}$$

### ۲. بلاکچین هایپرکیوب ۸D

*   **HypercubeBlockchain** با ۸ مختصه منحصربه‌فرد
*   **HyperBlock** — بلاک‌های ۸ بعدی
*   **HyperTransaction** — تراکنش‌های فضایی
*   **Smart Contract VM** — اجرای قراردادهای هوشمند
*   **اجماع PoHD (Proof of HyperDistance)** + PoA + PoV

### ۳. متاورس ۸D

*   **HypercubeVisualizer** — 256 رأس، 1024 یال، چند استراتژی projection
*   **MetaverseWorld** — Entity، Avatar، Region، Vector3
*   **Space Manager** — مدیریت فضای ۸D
*   **Position Tracker** — ردیابی موقعیت SCDA در فضا

### ۴. امنیت پیشرفته

*   **AdvancedLogger** — لاگ رمزنگاری‌شده + audit trail
*   **EnhancedSecurityManager** — SecurityLevel + ThreatLevel + MFA + JWT
*   **NeuralSecuritySystem** — سیستم ایمنی ۵-حالته با pattern recogniser عصبی
*   **RateLimiter** — sliding-window + token-bucket

### ۵. بازار دانش و اقتصاد

*   **KnowledgeMarketplace** — توکن‌سازی دانش + Trading Engine + Escrow
*   **NFT Marketplace** — mint + list + buy
*   **DeFi Swap** — Pool LANA-USDC + AMM
*   **Token System** — LANA native token

### ۶. شبکه P2P غیرمتمرکز

*   **DHT (Kademlia)** — K-Bucket + RoutingTable + DHTNode
*   **P2PManager** — WebSocket transport
*   **WebSocket Gateway** — `/ws/{connection_type}/{connection_id}`
*   **Cross-Chain Bridge** — انتقال بین زنجیره‌ای

### ۷. هوش مصنوعی

*   **KEA (Knowledge Extraction Agent)** — استخراج دانش
*   **Problem Discovery Engine** — کشف مسائل سخت
*   **Solution Evaluator** — ارزیابی راه‌حل
*   **Dual Validation** — اعتبارسنجی دوگانه
*   **LLM Integration** — GPT-4, Gemini, Claude

### ۸. حکمرانی و تمدن

*   **DAO** — پیشنهادات + رأی‌گیری + quorum
*   **Diplomacy System** — اتحادها + reputation
*   **Civilization Manager** — مدیریت تمدن‌ها
*   **Achievement System** — سیستم دستاوردها

---

## 🏗️ معماری و ساختار پروژه

```
laniakea-protocol/
├── main.py                     # Entry point (Render)
├── laniakea/                   # بسته اصلی (34 زیرپوشه)
│   ├── core/                   # HypercubeBlockchain, SCDA Integration, VM
│   ├── intelligence/           # SCDA (3 نسخه), AI, Neural, ML
│   ├── metaverse/              # HypercubeVisualizer, World
│   ├── network/                # DHT, P2P, API router
│   ├── security/               # Logger, MFA, Neural, RateLimiter
│   ├── api/                    # FastAPI (82 routes)
│   ├── blockchain/             # Core, Mining
│   ├── consensus/              # PoA, PoHD, PoV
│   ├── governance/             # DAO, Diplomacy
│   ├── marketplace/            # Knowledge Market, NFT, Exchange
│   ├── crosschain/             # Bridge (3 ماژول)
│   ├── evolution/              # Evolution Manager
│   ├── websocket/              # Manager, Realtime, Notification
│   ├── quantum/                # Processor, Quantum System
│   ├── simulation/             # Cosmic, SCDA Simulator
│   ├── dashboard/              # Live, Advanced, Metrics
│   ├── identity/, achievements/, ai/, analytics/, cli/, defi/,
│   ├── external_apis/, monitoring/, oracles/, optimization/,
│   ├── problems/, reputation/, social/, storage/, utils/
├── docs/                       # ARCHITECTURE, WHITEPAPER, USER_MANUAL, ...
├── web/                        # Frontend (UI/UX)
├── tests/                      # pytest
├── examples/                   # SCDA simulation
├── monitoring/                 # Prometheus + Grafana
├── nginx/                      # Reverse proxy
├── deploy.sh, Dockerfile, docker-compose.yml
└── requirements.txt, pyproject.toml, config.yaml
```

**آمار:**
*   📦 **34** زیرپوشه‌ی اصلی
*   🐍 **120+** ماژول Python
*   🌐 **82** API endpoint
*   🛣️ **۸** WebSocket route
*   🧪 **۱۰** ماژول حیاتی بازگردانده‌شده از cleanup

---

## 🚀 نصب و راه‌اندازی

### پیش‌نیازها
*   Python 3.11.9 (پین شده در `runtime.txt`)
*   PostgreSQL 14+ (production) یا SQLite (development)
*   Redis 6+ (rate limiting)
*   Node.js 18+ (frontend build)

### Development

```bash
# 1. کلون
git clone https://github.com/QalamHipHop/laniakea-protocol.git
cd laniakea-protocol

# 2. محیط مجازی
python3 -m venv .venv
source .venv/bin/activate

# 3. وابستگی‌ها
pip install -r requirements.txt

# 4. تنظیمات
cp .env.example .env
# ویرایش DATABASE_URL, REDIS_URL و سایر مقادیر

# 5. اجرا
python main.py
# یا
uvicorn laniakea.api.main:app --reload --port 8000
```

### Production (Docker)

```bash
docker-compose up -d
```

### Production (Render)

پروژه از قبل روی Render مستقر است:
*   **Service ID:** `srv-d4683hali9vc73dc6c4g`
*   **URL:** https://laniakea-protocol.onrender.com
*   **Health:** https://laniakea-protocol.onrender.com/health

---

## 📡 API Endpoints (۸۲ مسیر)

### Core
*   `GET /` — صفحه اصلی
*   `GET /health` — بررسی سلامت (با cache)
*   `GET /core/status` — وضعیت هسته
*   `GET /version` — نسخه
*   `GET /discovery` — discovery endpoints (با cache)

### Blockchain
*   `GET /blockchain/info` — اطلاعات بلاکچین
*   `GET /blockchain/chain` — زنجیره
*   `POST /blockchain/mine` — استخراج
*   `POST /blockchain/transactions/new` — تراکنش جدید

### Token & DeFi
*   `GET /token/info` — اطلاعات توکن LANA
*   `GET /defi/pools` — استخرهای نقدینگی
*   `POST /defi/swap` — سواپ

### SCDA
*   `POST /scda/create` — ساخت SCDA جدید
*   `GET /scda/{identity}` — دریافت SCDA
*   `GET /scda/state/{identity}` — وضعیت
*   `POST /scda/solve` — حل مسئله
*   `GET /scda/leaderboard` — برترین‌ها
*   `GET /scda/knowledge-vector/{identity}` — بردار دانش

### Governance
*   `GET /governance/proposals` — پیشنهادات
*   `POST /governance/proposals/new` — ایجاد پیشنهاد
*   `POST /governance/proposals/{id}/vote` — رأی
*   `POST /governance/proposals/{id}/finalize` — نهایی‌سازی

### Knowledge Market
*   `GET /knowledge_market/types` — انواع دانش
*   `POST /knowledge_market/tokenize` — توکن‌سازی
*   `POST /knowledge_market/list` — لیست کردن
*   `POST /knowledge_market/buy` — خرید
*   `GET /knowledge_market/asset/{id}` — جزئیات دارایی

### Diplomacy
*   `GET /diplomacy/alliances` — اتحادها
*   `POST /diplomacy/alliance` — ایجاد اتحاد
*   `GET /diplomacy/stats` — آمار

### AI
*   `POST /ai/query` — پرسش از AI
*   `POST /ai/train` — آموزش

### Achievements
*   `GET /achievements/all`
*   `GET /achievements/user/{user_id}`
*   `GET /achievements/catalog`

### Cross-Chain
*   `GET /crosschain/supported` — زنجیره‌های پشتیبانی‌شده
*   `POST /crosschain/transfer/initiate`
*   `POST /crosschain/transfer/complete/{tx_id}`

### Quantum
*   `POST /quantum/job/submit`
*   `POST /quantum/job/process`

### WebSocket
*   `WS /ws/{connection_type}/{connection_id}` — Real-time updates

### Observability
*   `GET /dashboard/metrics`
*   `GET /dashboard/history/{key}`
*   `GET /observability/requests`
*   `GET /ws/stats`

📚 **مستندات کامل تعاملی:** `/docs` (Swagger UI) · `/redoc`

---

## 🧪 تست

```bash
# سریع
python test_quick.py

# Smoke test (production-like)
python smoke_test.py

# کامل با pytest
pytest tests/ -v
```

---

## 🛠️ توسعه

```bash
# فرمت
black laniakea/ tests/

# lint
flake8 laniakea/ tests/

# type-check
mypy laniakea/
```

---

## 📊 مانیتورینگ

*   **Prometheus:** `monitoring/prometheus.yml`
*   **Grafana:** `monitoring/grafana/`
*   **Locust:** `locustfile.py` (load testing)

---

## 🤝 مشارکت

از مشارکت استقبال می‌کنیم! لطفاً [`CONTRIBUTING.md`](./CONTRIBUTING.md) را مطالعه کنید.

---

## 📜 مجوز

MIT — تمامی حقوق برای **LaniakeA Dev** محفوظ است.

---

## 🌟 تیم

**LaniakeA Dev Team** — ساخته شده با ❤️ برای آینده‌ای غیرمتمرکز.

---

<div align="center">

**[⬆️ بازگشت به بالا](#laniakea-protocol-the-cosmic-evolution-engine)**

ساخته شده توسط **LaniakeA Dev** · Live at [laniakea-protocol.onrender.com](https://laniakea-protocol.onrender.com)

</div>

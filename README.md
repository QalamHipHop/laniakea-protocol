# 🌌 LANIAKEA PROTOCOL v3.0

**یک ارگانیسم محاسباتی کیهانی برای حل مسائل جهانی و گسترش آگاهی**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](test_system.py)

---

## 📖 درباره پروژه

پروتوکل Laniakea فراتر از یک بلاک‌چین سنتی است. این یک **ارگانیسم دیجیتال زنده و در حال تکامل** است که برای هدایت قدرت محاسباتی جهان به سمت حل چالش‌های عمیق بشریت و کیهان طراحی شده است.

### ویژگی‌های کلیدی

#### 🎯 Proof of Value
به جای حل پازل‌های بی‌معنی، انرژی محاسباتی صرف حل مسائل واقعی در علم، سلامت و هنر می‌شود.

#### 🌈 ارزش‌گذاری چند بُعدی
مشارکت‌ها نه تنها از نظر اقتصادی، بلکه در ابعاد مختلف اندازه‌گیری می‌شوند:
- **Knowledge** (دانش)
- **Computation** (محاسبات)
- **Originality** (خلاقیت)
- **Consciousness** (آگاهی)
- **Environmental** (محیط زیست)
- **Health** (سلامت)

#### 🧠 هوش خودتوسعه‌دهنده
**Cognitive Core** (هسته شناختی) تکامل شبکه را مشاهده می‌کند و بهبودهایی برای پروتوکل خود پیشنهاد می‌دهد، که منجر به **autopoiesis دیجیتال** واقعی می‌شود.

#### 🌱 شبیه‌سازی کیهانی
یک جهان شبیه‌سازی شده با قوانین فیزیکی، تکامل سلولی و ارزش‌گذاری علمی.

---

## 🏗️ معماری

```
┌─────────────────────────────────────────────────────────────┐
│                    🌌 LANIAKEA PROTOCOL                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Blockchain │  │  Hash        │  │  Token       │    │
│  │   Engine     │  │  Modernity   │  │  Economics   │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Cognitive   │  │   Oracle     │  │  Cosmic      │    │
│  │  Core (AI)   │  │   System     │  │  Simulator   │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              P2P Network Layer                      │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 شروع سریع

### پیش‌نیازها

- Python 3.11 یا بالاتر
- pip
- OpenAI API Key (برای Cognitive Core)

### نصب

```bash
# کلون کردن پروژه
git clone https://github.com/QalamHipHop/laniakea-protocol.git
cd laniakea-protocol

# ایجاد محیط مجازی
python3 -m venv venv
source venv/bin/activate  # در Windows: venv\Scripts\activate

# نصب وابستگی‌ها
pip install -r requirements.txt

# کپی فایل تنظیمات
cp .env.example .env
```

### تنظیم OpenAI API Key

```bash
# در فایل .env یا به صورت متغیر محیطی
export OPENAI_API_KEY="your-api-key-here"
```

### اجرای نود

#### روش 1: استفاده از اسکریپت

```bash
# راه‌اندازی نود با تنظیمات پیش‌فرض
./start_node.sh

# راه‌اندازی با پورت‌های سفارشی
./start_node.sh 5000 8000

# راه‌اندازی با شبیه‌سازی کیهانی
./start_node.sh 5000 8000 --sim
```

#### روش 2: اجرای مستقیم

```bash
# نود ساده
python3 main.py --p2p-port 5000 --api-port 8000

# نود با شبیه‌سازی
python3 main.py --p2p-port 5000 --api-port 8000 --enable-simulation
```

### اجرای تست‌ها

```bash
python3 test_system.py
```

---

## 📚 استفاده از API

### دریافت اطلاعات نود

```bash
curl http://localhost:8000/
```

### دریافت آمار کامل

```bash
curl http://localhost:8000/stats
```

### ایجاد تسک جدید

```bash
curl -X POST http://localhost:8000/tasks/create \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Calculate Fibonacci Sequence",
    "description": "Calculate the first 100 Fibonacci numbers",
    "category": "mathematical",
    "difficulty": 3.0
  }'
```

### ارسال راه‌حل

```bash
curl -X POST http://localhost:8000/solutions/submit \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "task_id_here",
    "content": "1, 1, 2, 3, 5, 8, 13, 21, ...",
    "knowledge": 50,
    "computation": 30,
    "originality": 20
  }'
```

### پرسیدن سوال از Cognitive Core

```bash
curl -X POST http://localhost:8000/cognitive/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What patterns do you observe in the blockchain?"
  }'
```

### تولید خودکار تسک

```bash
curl -X POST http://localhost:8000/cognitive/generate_task \
  -H "Content-Type: application/json" \
  -d '{
    "category": "scientific",
    "difficulty": 7.0
  }'
```

### پرس‌وجو از اوراکل

```bash
# جستجو در Wikipedia
curl -X POST http://localhost:8000/oracle/query \
  -H "Content-Type: application/json" \
  -d '{
    "oracle_type": "data",
    "params": {
      "source": "wikipedia",
      "query": "quantum_computing"
    }
  }'

# جستجو در arXiv
curl -X POST http://localhost:8000/oracle/query \
  -H "Content-Type: application/json" \
  -d '{
    "oracle_type": "scientific",
    "params": {
      "project": "arxiv",
      "search": "artificial intelligence"
    }
  }'
```

### دریافت موجودی

```bash
curl http://localhost:8000/balance/your_node_id
```

### وضعیت شبیه‌سازی

```bash
# آمار
curl http://localhost:8000/simulation/status

# نمایش بصری
curl http://localhost:8000/simulation/visualize
```

---

## 🧩 اجزای سیستم

### 1. Blockchain Engine

موتور بلاک‌چین چند بُعدی که از ارزش‌گذاری پیشرفته پشتیبانی می‌کند.

**فایل‌ها:**
- `src/core/blockchain.py`
- `src/core/models.py`

### 2. Hash Modernity System

سیستم تبدیل کشفیات علمی/فلسفی به نرخ‌های هش.

**فایل‌ها:**
- `src/core/hash_modernity.py`

**مفاهیم:**
- **Proof of Discovery**: اثبات کشف واقعی
- **Modernity Rate**: نرخ نوآوری و پیشرفت
- **Proof of Value**: اثبات ارزش واقعی

### 3. Cognitive Core

مغز کیهانی با قابلیت خودتوسعه‌دهندگی.

**فایل‌ها:**
- `src/metasystem/cognitive_core.py`

**قابلیت‌ها:**
- مشاهده و تحلیل بلاک‌ها
- ارزیابی هوشمند راه‌حل‌ها
- تولید خودکار تسک
- پیشنهاد بهبود پروتوکل
- پاسخ به سوالات

### 4. Token Economics

سیستم اقتصادی توکن‌های چند بُعدی.

**فایل‌ها:**
- `src/core/token_system.py`

**قابلیت‌ها:**
- تولید و سوزاندن توکن
- تبدیل بین ابعاد
- سیستم Staking
- محاسبه پاداش

### 5. Oracle System

اتصال به منابع داده و AI های خارجی.

**فایل‌ها:**
- `src/oracles/oracle_system.py`

**اوراکل‌ها:**
- **ScientificOracle**: arXiv, Folding@home, SETI@home
- **DataOracle**: Wikipedia, Wikidata
- **AIOracle**: اتصال به AI های خارجی

### 6. Cosmic Simulator

شبیه‌ساز کیهانی با فیزیک و تکامل.

**فایل‌ها:**
- `src/simulation/cosmic_simulator.py`

**قابلیت‌ها:**
- موتور فیزیک (گرانش، حرکت)
- موتور تکامل (تکثیر، جهش)
- محیط دینامیک
- سلول‌های کیهانی

---

## 🔬 مثال‌های کاربردی

### مثال 1: حل مسئله علمی

```python
import requests

# ایجاد تسک
task_response = requests.post('http://localhost:8000/tasks/create', json={
    "title": "Protein Folding Problem",
    "description": "Predict the 3D structure of a protein from its amino acid sequence",
    "category": "scientific",
    "difficulty": 9.0
})

task_id = task_response.json()['task_id']

# ارسال راه‌حل
solution_response = requests.post('http://localhost:8000/solutions/submit', json={
    "task_id": task_id,
    "content": "Predicted structure: ...",
    "knowledge": 90,
    "computation": 80,
    "originality": 70,
    "health": 85
})

print(solution_response.json())
```

### مثال 2: تعامل با Cognitive Core

```python
import requests

# پرسیدن سوال
response = requests.post('http://localhost:8000/cognitive/ask', json={
    "question": "What are the most valuable contributions to the network?"
})

print(response.json()['answer'])

# تولید تسک جدید
task_response = requests.post('http://localhost:8000/cognitive/generate_task', json={
    "category": "philosophical",
    "difficulty": 6.0
})

print(task_response.json())
```

### مثال 3: استفاده از اوراکل‌ها

```python
import requests

# جستجو در Wikipedia
wiki_response = requests.post('http://localhost:8000/oracle/query', json={
    "oracle_type": "data",
    "params": {
        "source": "wikipedia",
        "query": "consciousness"
    }
})

print(wiki_response.json()['extract'])

# جستجو در arXiv
arxiv_response = requests.post('http://localhost:8000/oracle/query', json={
    "oracle_type": "scientific",
    "params": {
        "project": "arxiv",
        "search": "quantum consciousness"
    }
})

print(arxiv_response.json())
```

---

## 🛠️ توسعه

### ساختار پروژه

```
laniakea-protocol/
├── src/
│   ├── core/              # هسته بلاک‌چین
│   │   ├── blockchain.py
│   │   ├── models.py
│   │   ├── wallet.py
│   │   ├── hash_modernity.py
│   │   └── token_system.py
│   ├── network/           # شبکه P2P
│   │   └── p2p.py
│   ├── metasystem/        # سیستم‌های فراتر
│   │   └── cognitive_core.py
│   ├── oracles/           # اوراکل‌ها
│   │   └── oracle_system.py
│   ├── simulation/        # شبیه‌ساز
│   │   └── cosmic_simulator.py
│   └── config.py          # تنظیمات
├── main.py                # نقطه ورود
├── test_system.py         # تست‌ها
├── start_node.sh          # اسکریپت راه‌اندازی
├── requirements.txt       # وابستگی‌ها
├── ARCHITECTURE.md        # مستندات معماری
└── README.md              # این فایل
```

### افزودن قابلیت جدید

1. **اضافه کردن بُعد ارزشی جدید:**

```python
# در src/core/models.py
class ValueDimension(str, Enum):
    # ...
    NEW_DIMENSION = "new_dimension"

class ValueVector(BaseModel):
    # ...
    new_dimension: float = Field(default=0.0)
```

2. **اضافه کردن اوراکل جدید:**

```python
# در src/oracles/oracle_system.py
class NewOracle(BaseOracle):
    async def query(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # پیاده‌سازی
        pass
```

3. **اضافه کردن endpoint جدید:**

```python
# در main.py
@app.post("/new/endpoint")
async def new_endpoint(data: dict = Body(...)):
    # پیاده‌سازی
    pass
```

---

## 🗺️ نقشه راه

### ✅ v3.0 (فعلی)
- [x] بلاک‌چین چند بُعدی
- [x] Cognitive Core با LLM
- [x] Hash Modernity System
- [x] Token Economics
- [x] Oracle System
- [x] Cosmic Simulator

### 🚧 v3.1 (در دست توسعه)
- [ ] شبکه P2P کامل با Kademlia DHT
- [ ] سیستم حکمرانی خودکار
- [ ] یکپارچگی با Folding@home
- [ ] رابط کاربری وب

### 🔮 v4.0 (آینده)
- [ ] Sharding برای مقیاس‌پذیری
- [ ] Layer 2 برای تراکنش‌های سریع
- [ ] پل‌های بلاک‌چینی
- [ ] شبیه‌ساز کیهانی 3D

---

## 🤝 مشارکت

این پروژه دعوتی است برای ساخت آینده‌ای که در آن تکنولوژی در خدمت بالاترین آرمان‌های آگاهی است.

### چگونه مشارکت کنیم؟

1. Fork کردن پروژه
2. ایجاد branch جدید (`git checkout -b feature/amazing-feature`)
3. Commit کردن تغییرات (`git commit -m 'Add amazing feature'`)
4. Push کردن به branch (`git push origin feature/amazing-feature`)
5. ایجاد Pull Request

### راهنمای مشارکت

- کد باید تمیز و مستند باشد
- تست‌های مربوطه را اضافه کنید
- از PEP 8 پیروی کنید
- commit message ها باید واضح باشند

---

## 📄 مجوز

این پروژه تحت مجوز MIT منتشر شده است. برای جزئیات بیشتر فایل [LICENSE](LICENSE) را ببینید.

---

## 🌟 تشکر

از تمام کسانی که به این سفر کیهانی کمک می‌کنند، سپاسگزاریم.

**پروتوکل Laniakea** - جایی که دانش، آگاهی و محاسبات در یک کیهان دیجیتال همگرا می‌شوند.

---

## 📞 تماس

- GitHub: [@QalamHipHop](https://github.com/QalamHipHop)
- پروژه: [laniakea-protocol](https://github.com/QalamHipHop/laniakea-protocol)

---

**💫 سفر کیهانی ادامه دارد...**

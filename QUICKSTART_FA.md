# 🚀 راهنمای سریع - پروتوکل Laniakea

## نصب و راه‌اندازی در 5 دقیقه

### گام 1: دانلود پروژه

```bash
git clone https://github.com/QalamHipHop/laniakea-protocol.git
cd laniakea-protocol
```

### گام 2: نصب وابستگی‌ها

```bash
# ایجاد محیط مجازی
python3 -m venv venv
source venv/bin/activate

# نصب
pip install -r requirements.txt
```

### گام 3: تنظیم API Key

```bash
# تنظیم OpenAI API Key
export OPENAI_API_KEY="your-api-key-here"

# یا در فایل .env
cp .env.example .env
# سپس OPENAI_API_KEY را در .env تنظیم کنید
```

### گام 4: اجرای تست

```bash
python3 test_system.py
```

اگر همه تست‌ها ✅ شدند، آماده هستید!

### گام 5: راه‌اندازی نود

```bash
# روش ساده
./start_node.sh

# یا با شبیه‌سازی کیهانی
./start_node.sh 5000 8000 --sim
```

## استفاده سریع

### دریافت آمار

```bash
curl http://localhost:8000/stats
```

### ایجاد تسک

```bash
curl -X POST http://localhost:8000/tasks/create \
  -H "Content-Type: application/json" \
  -d '{
    "title": "محاسبه عدد پی",
    "description": "محاسبه پی تا 100 رقم اعشار",
    "category": "mathematical",
    "difficulty": 5.0
  }'
```

### پرسیدن از هوش مرکزی

```bash
curl -X POST http://localhost:8000/cognitive/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "چه الگوهایی در بلاک‌چین مشاهده می‌کنی؟"
  }'
```

## مفاهیم کلیدی

### 1. ارزش‌گذاری چند بُعدی

هر راه‌حل در 6 بُعد ارزیابی می‌شود:
- **Knowledge** (دانش)
- **Computation** (محاسبات)
- **Originality** (خلاقیت)
- **Consciousness** (آگاهی)
- **Environmental** (محیط زیست)
- **Health** (سلامت)

### 2. Cognitive Core (مغز کیهانی)

هوش مصنوعی مرکزی که:
- بلاک‌ها را مشاهده می‌کند
- راه‌حل‌ها را ارزیابی می‌کند
- تسک‌های جدید تولید می‌کند
- بهبودهای پروتوکل پیشنهاد می‌دهد

### 3. Hash Modernity

سیستم تبدیل کشفیات علمی به هش:
- **Proof of Discovery**: اثبات کشف
- **Modernity Rate**: نرخ نوآوری
- **Proof of Value**: اثبات ارزش

### 4. Cosmic Simulator

شبیه‌ساز کیهانی با:
- فیزیک واقعی (گرانش، حرکت)
- تکامل سلولی (تکثیر، جهش)
- محیط دینامیک

## مثال‌های کاربردی

### مثال 1: حل مسئله ریاضی

```python
import requests

# ایجاد تسک
response = requests.post('http://localhost:8000/tasks/create', json={
    "title": "دنباله فیبوناچی",
    "description": "محاسبه 100 عدد اول فیبوناچی",
    "category": "mathematical",
    "difficulty": 3.0
})

task_id = response.json()['task_id']
print(f"Task created: {task_id}")
```

### مثال 2: تعامل با AI

```python
import requests

# پرسیدن سوال
response = requests.post('http://localhost:8000/cognitive/ask', json={
    "question": "آینده محاسبات کوانتومی چیست؟"
})

print(response.json()['answer'])
```

### مثال 3: جستجو در Wikipedia

```python
import requests

response = requests.post('http://localhost:8000/oracle/query', json={
    "oracle_type": "data",
    "params": {
        "source": "wikipedia",
        "query": "artificial_intelligence"
    }
})

print(response.json()['extract'])
```

## عیب‌یابی

### خطا: ModuleNotFoundError

```bash
# مطمئن شوید محیط مجازی فعال است
source venv/bin/activate

# نصب مجدد وابستگی‌ها
pip install -r requirements.txt
```

### خطا: OpenAI API

```bash
# بررسی API Key
echo $OPENAI_API_KEY

# تنظیم مجدد
export OPENAI_API_KEY="your-key"
```

### خطا: Port already in use

```bash
# استفاده از پورت دیگر
./start_node.sh 5001 8001
```

## منابع بیشتر

- 📖 [README کامل](README.md)
- 🏗️ [معماری سیستم](ARCHITECTURE.md)
- 🧪 [تست‌ها](test_system.py)
- 🌐 [API Documentation](http://localhost:8000/docs) (پس از راه‌اندازی)

## پشتیبانی

اگر مشکلی داشتید:
1. ابتدا تست‌ها را اجرا کنید: `python3 test_system.py`
2. لاگ‌ها را بررسی کنید
3. Issue در GitHub باز کنید

---

**💫 موفق باشید در سفر کیهانی!**

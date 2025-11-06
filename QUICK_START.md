# 🚀 Laniakea Protocol - Quick Start Guide

راهنمای سریع برای شروع کار با پروتکل Laniakea v0.0.02

## ⚡ شروع سریع

### ۱. راه‌اندازی خودکار
```bash
# کلون ریپازیتوری
git clone https://github.com/QalamHipHop/laniakea-protocol.git
cd laniakea-protocol

# راه‌اندازی خودکار (پیشنهادی)
python start.py
```

### ۲. راه‌اندازی دستی
```bash
# نصب وابستگی‌ها
pip install -r requirements.txt

# اجرا
python main.py --node-id my-node --port 8000
```

### ۳. با Docker
```bash
# ساخت و اجرا
make docker-compose-up

# یا دستی
docker-compose up -d
```

## 🌐 دسترسی به سیستم

- **داشبورد اصلی**: http://localhost:8000
- **مستندات API**: http://localhost:8000/docs
- **بررسی سلامت**: http://localhost:8000/health
- **وضعیت کامل**: http://localhost:8000/status

## 🛠️ دستورات مفید

```bash
# اطلاعات پروژه
make info

# اجرا در حالت توسعه
make dev

# تست‌ها
make test

# لاگ‌ها
make logs

# بررسی سلامت
make health

# تمیزکاری
make clean
```

## 📱 حالت‌های اجرا

### حالت پیشرفته (Enhanced)
```bash
python main.py --node-id my-node --port 8000
```
- 🧠 هوش مصنوعی کیهانی
- 🛡️ امنیت عصبی
- ⚡ بهینه‌سازی خودکار
- 🌐跨链兼容ibility

### حالت حداقلی (Minimal)
```bash
python main.py --node-id my-node --port 8000 --disable-enhanced
```
- ⚡ عملکرد سریع
- 📦 منابع کمتر
- 🔒 امنیت پایه
- 📱 مناسب برای موبایل

## 🔧 پیکربندی

فایل `.env` را ایجاد کنید:
```bash
NODE_ID=my-node
HOST=0.0.0.0
PORT=8000
OPENAI_API_KEY=your-key-here
```

## 🚀 Production Deployment

```bash
# Deploy به production
make deploy-prod

# یا با Docker
docker-compose -f docker-compose.yml up -d
```

## 📞 راهنما و پشتیبانی

- 📚 **مستندات کامل**: [DOCUMENTATION.md](./DOCUMENTATION.md)
- 🔧 **راهنمای توسعه**: [docs/guides/](./docs/guides/)
- 🐳 **Docker guide**: [docs/deployment/](./docs/deployment/)
- 📡 **API Examples**: [docs/api/](./docs/api/)

---

<div align="center">

**🌌 Laniakea Protocol v0.0.02**

*موفق باشید!*

</div>
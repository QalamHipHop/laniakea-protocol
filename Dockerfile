# Laniakea Protocol - Production Docker Image
FROM python:3.11-slim

# متادیتا
LABEL maintainer="Laniakea Protocol Team"
LABEL version="0.0.1"
LABEL description="A cosmic computational organism for universal problem-solving"

# متغیرهای محیطی
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# نصب وابستگی‌های سیستمی
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ایجاد دایرکتوری کاری
WORKDIR /app

# کپی فایل‌های requirements
COPY requirements.txt .

# نصب وابستگی‌های Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# کپی کل پروژه
COPY . .

# ایجاد دایرکتوری‌های مورد نیاز
RUN mkdir -p /app/data /app/logs

# پورت‌های قابل دسترسی
EXPOSE 8000 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# دستور اجرا
CMD ["python3", "main.py", "--p2p-port", "5000", "--api-port", "8000"]

#!/bin/bash

# Laniakea Protocol v5.0 - Node Startup Script
# اسکریپت راه‌اندازی نود نسخه 5.0

echo "🌌 Starting Laniakea Protocol v5.0..."

# تنظیم متغیرهای محیطی (در صورت نیاز)
export OPENAI_API_KEY="${OPENAI_API_KEY:-your_key_here}"
export NASA_API_KEY="${NASA_API_KEY:-DEMO_KEY}"

# پارامترهای پیش‌فرض
P2P_PORT="${1:-5000}"
API_PORT="${2:-8000}"
ENABLE_SIM="${3:-}"

# ساخت دایرکتوری داده
mkdir -p "data_node_${P2P_PORT}"

# راه‌اندازی نود
if [ "$ENABLE_SIM" == "--sim" ]; then
    echo "🌠 Starting with cosmic simulation..."
    python3 main_v5.py --p2p-port "$P2P_PORT" --api-port "$API_PORT" --enable-simulation
else
    python3 main_v5.py --p2p-port "$P2P_PORT" --api-port "$API_PORT"
fi

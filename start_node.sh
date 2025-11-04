#!/bin/bash

# Laniakea Protocol v0.0.1 - Node Startup Script
# اسکریپت راه‌اندازی نود نسخه 0.0.1

echo "🌌 Starting Laniakea Protocol v0.0.1..."

# تنظیم متغیرهای محیطی (در صورت نیاز)
export OPENAI_API_KEY="${OPENAI_API_KEY:-your_key_here}"
export NASA_API_KEY="${NASA_API_KEY:-DEMO_KEY}"

# پارامترهای پیش‌فرض
P2P_PORT="${1:-5000}"
API_PORT="${2:-8000}"
SIM_FLAG=""
if [ "$3" == "--enable-simulation" ]; then
    SIM_FLAG="--enable-simulation"
fi

# ساخت دایرکتوری داده
mkdir -p "data_node_${P2P_PORT}"

# راه‌اندازی نود
# اجرای نود اصلی در پس‌زمینه
echo "🚀 Starting Laniakea Node..."
python3 main.py --p2p-port "$P2P_PORT" --api-port "$API_PORT" $SIM_FLAG &
NODE_PID=$!

# اجرای حلقه توسعه درونی دائمی
echo "🧠 Starting Laniakea Self-Evolution Loop..."
python3 self_evolution_loop.py &
EVO_PID=$!

# منتظر ماندن برای پایان فرآیندها
wait $NODE_PID $EVO_PID

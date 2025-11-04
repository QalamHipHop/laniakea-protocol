#!/bin/bash

# Laniakea Protocol - Node Startup Script

echo "🌌 Starting Laniakea Protocol Node..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file..."
    cp .env.example .env
    echo "IS_AUTHORITY=true" >> .env
fi

# Default ports
P2P_PORT=${1:-5000}
API_PORT=${2:-8000}
ENABLE_SIM=${3:-""}

echo ""
echo "🚀 Launching node..."
echo "   P2P Port: $P2P_PORT"
echo "   API Port: $API_PORT"
echo ""

# Run the node
if [ "$ENABLE_SIM" = "--sim" ]; then
    python3 main.py --p2p-port $P2P_PORT --api-port $API_PORT --enable-simulation
else
    python3 main.py --p2p-port $P2P_PORT --api-port $API_PORT
fi

#!/usr/bin/env bash
# ============================================================
# Laniakea Protocol — Local dev runner
# Starts API (FastAPI/uvicorn) + Vite dev server in one shot.
# Usage:  bash scripts/dev.sh
#         bash scripts/dev.sh --api-only
#         bash scripts/dev.sh --web-only
# ============================================================
set -euo pipefail

cd "$(dirname "$0")/.."

API_HOST="${API_HOST:-0.0.0.0}"
API_PORT="${API_PORT:-8000}"
WEB_PORT="${WEB_PORT:-5173}"
LOG_DIR="${LOG_DIR:-./logs}"
mkdir -p "$LOG_DIR"

PYTHON="${PYTHON:-python3}"
VITE="${VITE:-npx vite}"

cleanup() {
  echo
  echo "🛑 Shutting down..."
  if [[ -n "${API_PID:-}" ]]; then kill "$API_PID" 2>/dev/null || true; fi
  if [[ -n "${WEB_PID:-}" ]]; then kill "$WEB_PID" 2>/dev/null || true; fi
  wait 2>/dev/null || true
  echo "👋 Done."
}
trap cleanup INT TERM

start_api() {
  echo "🚀 Starting API on http://$API_HOST:$API_PORT"
  "$PYTHON" main.py --host "$API_HOST" --port "$API_PORT" \
    > "$LOG_DIR/api.log" 2>&1 &
  API_PID=$!
  echo "   pid=$API_PID  log=$LOG_DIR/api.log"
}

start_web() {
  echo "🎨 Starting Vite on http://localhost:$WEB_PORT"
  (cd web && $VITE --port "$WEB_PORT" --host 0.0.0.0) \
    > "$LOG_DIR/web.log" 2>&1 &
  WEB_PID=$!
  echo "   pid=$WEB_PID  log=$LOG_DIR/web.log"
}

MODE="${1:-all}"
case "$MODE" in
  --api-only|api)   start_api ;;
  --web-only|web)   start_web ;;
  all|"")           start_api; start_web ;;
  *) echo "Unknown mode: $MODE"; exit 1 ;;
esac

echo
echo "🌌 Laniakea running. Press Ctrl+C to stop."
echo "   API  → http://localhost:$API_PORT/health"
echo "   UI   → http://localhost:$WEB_PORT/"
echo
wait

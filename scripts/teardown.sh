#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PID_DIR="/tmp/integrador"

# ── Frontend ──────────────────────────────────────────────────────────────────
echo "==> Stopping frontend"
if [ -f "$PID_DIR/frontend.pid" ]; then
  kill "$(cat "$PID_DIR/frontend.pid")" 2>/dev/null || true
  rm -f "$PID_DIR/frontend.pid"
fi
fuser -k 3000/tcp 2>/dev/null || true

# ── Backend ───────────────────────────────────────────────────────────────────
echo "==> Stopping backend"
if [ -f "$PID_DIR/backend.pid" ]; then
  kill "$(cat "$PID_DIR/backend.pid")" 2>/dev/null || true
  rm -f "$PID_DIR/backend.pid"
fi
fuser -k 8000/tcp 2>/dev/null || true

# ── Observability ─────────────────────────────────────────────────────────────
echo "==> Stopping observability stack"
cd "$ROOT/observability"
docker-compose --profile local-prometheus down

# ── Database ──────────────────────────────────────────────────────────────────
echo "==> Stopping PostgreSQL"
cd "$ROOT/apps/backend"
docker-compose down

echo ""
echo "All services stopped."

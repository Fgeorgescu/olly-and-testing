#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PID_DIR="/tmp/integrador"

mkdir -p "$PID_DIR"

# ── Database ─────────────────────────────────────────────────────────────────
echo "==> Starting PostgreSQL"
cd "$ROOT/apps/backend"
docker-compose up -d db

# ── Observability ─────────────────────────────────────────────────────────────
echo "==> Starting observability stack (Prometheus, Loki, Promtail, Grafana)"
cd "$ROOT/observability"
if [ -n "${PROMETHEUS_URL:-}" ]; then
  echo "    PROMETHEUS_URL set — starting Grafana + Loki only"
  docker-compose up -d grafana loki promtail
else
  docker-compose --profile local-prometheus up -d
fi

# ── Dependencies ──────────────────────────────────────────────────────────────
echo "==> Installing backend dependencies"
cd "$ROOT/apps/backend"
uv sync --extra dev --quiet

echo "==> Installing frontend dependencies"
cd "$ROOT/apps/frontend"
npm install --prefer-offline --silent

# ── Backend ───────────────────────────────────────────────────────────────────
echo "==> Starting backend (port 8000)"
cd "$ROOT/apps/backend"
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 \
  > "$PID_DIR/backend.log" 2>&1 &
echo $! > "$PID_DIR/backend.pid"

# ── Frontend ──────────────────────────────────────────────────────────────────
echo "==> Starting frontend (port 3000)"
cd "$ROOT/apps/frontend"
npm run dev > "$PID_DIR/frontend.log" 2>&1 &
echo $! > "$PID_DIR/frontend.pid"

# ── Health check ──────────────────────────────────────────────────────────────
echo "==> Waiting for services to be ready..."
for i in $(seq 1 20); do
  if curl -sf http://localhost:8000/api/v1/health > /dev/null 2>&1 && \
     curl -sf http://localhost:3000 > /dev/null 2>&1; then
    break
  fi
  sleep 2
done

echo ""
echo "┌─────────────────────────────────────────────────┐"
echo "│  All services running                           │"
echo "├─────────────────────────────────────────────────┤"
echo "│  Frontend   → http://localhost:3000             │"
echo "│  Backend    → http://localhost:8000/docs        │"
echo "│  Grafana    → http://localhost:3001  (admin)    │"
echo "│  Prometheus → http://localhost:9090             │"
echo "│  Loki       → http://localhost:3100             │"
echo "├─────────────────────────────────────────────────┤"
echo "│  Logs:                                          │"
echo "│    tail -f $PID_DIR/backend.log                 │"
echo "│    tail -f $PID_DIR/frontend.log                │"
echo "└─────────────────────────────────────────────────┘"
echo ""
echo "Stop everything: make teardown"

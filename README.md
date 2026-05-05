# Integrador

A full-stack marketplace monorepo with a FastAPI backend, Next.js frontend, and a local observability stack (Prometheus + Loki + Grafana).

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Local dev environment                    │
│                                                                 │
│   ┌────────────┐   HTTP    ┌─────────────┐   SQL   ┌────────┐  │
│   │  Frontend  │ ────────▶ │   Backend   │ ──────▶ │  PG   │  │
│   │  (Next.js) │           │  (FastAPI)  │         │  DB   │  │
│   │  :3000     │           │  :8000      │         └────────┘  │
│   └────────────┘           └──────┬──────┘                     │
│                                   │ /metrics + logs/app.log    │
│                 ┌─────────────────┼──────────────────────┐     │
│                 │   Observability │ stack                 │     │
│                 │                 ▼                       │     │
│                 │  ┌──────────┐  ┌───────┐  ┌─────────┐  │     │
│                 │  │Prometheus│  │ Loki  │  │ Grafana │  │     │
│                 │  │  :9090   │  │ :3100 │  │  :3001  │  │     │
│                 │  └──────────┘  └───┬───┘  └─────────┘  │     │
│                 │                    │                     │     │
│                 │             ┌──────┘                     │     │
│                 │         ┌───▼────┐                       │     │
│                 │         │Promtail│ (scrapes logs/)       │     │
│                 │         └────────┘                       │     │
│                 └─────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

## Prerequisites

| Tool | Purpose |
|------|---------|
| [Docker](https://docs.docker.com/get-docker/) + docker-compose | Container runtime |
| [Python 3.11+](https://www.python.org/) + [uv](https://github.com/astral-sh/uv) | Backend runtime |
| [Node.js 18+](https://nodejs.org/) | Frontend runtime |

## Quick Start

```bash
# Start everything (DB, observability, backend, frontend)
make setup

# Stop everything
make teardown
```

That's it. `make setup` installs dependencies, starts all services, waits for health checks, and prints the URLs.

## URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | — |
| Backend API | http://localhost:8000/docs | — |
| Grafana | http://localhost:3001 | admin / admin |
| Prometheus | http://localhost:9090 | — |
| Loki | http://localhost:3100 | — |

## Components

| Component | Description | README |
|-----------|-------------|--------|
| Backend | FastAPI REST API with Prometheus metrics and structured logging | [apps/backend/README.md](apps/backend/README.md) |
| Frontend | Next.js marketplace UI | [apps/frontend/README.md](apps/frontend/README.md) |
| Observability | Prometheus + Loki + Grafana local stack | [observability/README.md](observability/README.md) |

## Repository Structure

```
integrador/
├── apps/
│   ├── backend/        # FastAPI service
│   └── frontend/       # Next.js app
├── observability/
│   ├── docker-compose.yml          # Prometheus, Loki, Promtail, Grafana
│   ├── prometheus.yml              # Scrape config
│   ├── loki/                       # Loki config
│   ├── promtail/                   # Promtail config
│   └── grafana/
│       ├── dashboards/             # Dashboard JSON files
│       └── provisioning/           # Auto-provisioned datasources + dashboards
├── infra/k8s/          # Kustomize manifests (Kubernetes deployment)
├── scripts/
│   ├── setup.sh        # Start all local services
│   └── teardown.sh     # Stop all local services
├── docs/adr/           # Architecture Decision Records
└── Makefile
```

## Makefile Reference

```bash
make setup              # Start all local services
make teardown           # Stop all local services

make backend-install    # Install backend Python dependencies
make backend-run        # Run backend with hot-reload (port 8000)
make backend-test       # Run all backend tests
make backend-test-unit  # Run unit tests only (no Docker required)
make backend-lint       # Lint and format-check backend

make db-up              # Start PostgreSQL only
make db-down            # Stop PostgreSQL

make obs-up             # Start observability stack only
make obs-down           # Stop observability stack
```

Set `PROMETHEUS_URL` to use an existing Prometheus instance — only Grafana and Loki will start:

```bash
PROMETHEUS_URL=http://my-prometheus:9090 make obs-up
```

## Architecture Decisions

Design decisions are documented as ADRs in [`docs/adr/`](docs/adr/).

| ADR | Decision |
|-----|----------|
| [001](docs/adr/001-backend-language.md) | Backend language: FastAPI (Python) |
| [002](docs/adr/002-persistence-layer.md) | Persistence: PostgreSQL + SQLAlchemy async + Alembic |
| [003](docs/adr/003-testing-strategy.md) | Testing: unit / integration / e2e tiers with repository pattern |

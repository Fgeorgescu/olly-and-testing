# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

### Full local environment
```bash
make setup          # Create kind cluster + install Prometheus & Grafana via Helm
make dev            # Skaffold watch loop: rebuilds images and redeploys on file change
make teardown       # Destroy the kind cluster
```

### Backend
```bash
make backend-install              # pip install -e ".[dev]" in apps/backend
make backend-run                  # uvicorn with --reload on port 8000
make backend-test                 # pytest
make backend-lint                 # ruff check + format check
cd apps/backend && pytest tests/test_health.py   # single test file
```

### Kubernetes
```bash
kubectl apply -k infra/k8s/overlays/local    # manually apply local manifests
kubectl port-forward svc/backend 8000:8000   # expose backend locally
```

### Observability access (after setup)
```bash
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80
kubectl port-forward -n monitoring svc/monitoring-kube-prometheus-prometheus 9090:9090
```

## Branching Model

| Branch | Purpose | Base |
|--------|---------|------|
| `main` | Production-ready code | — |
| `develop` | Staging; integration target for features | `main` |
| `feature/{issue_id}-{feature_name}` | One feature or related set of changes | `develop` |

**Workflow for every feature:**
1. Check for an existing GitHub issue (`gh issue list --repo Fgeorgescu/integrador`). If none exists, create one with a short title and description (`gh issue create`).
2. Branch off `develop`: `git checkout -b feature/{issue_id}-{feature_name} develop`
3. Open a PR targeting `develop` when done.
4. `develop` is merged into `main` for production releases.

Never commit feature work directly to `main` or `develop`.

## Skills (Slash Commands)

Project-specific skills live in `.claude/commands/`. See [`.claude/commands/README.md`](.claude/commands/README.md) for the full list and usage.

| Command | What it does |
|---------|-------------|
| `/fix-ci` | Diagnoses and fixes the most recent failing CI run, then pushes the fix |

## Architecture Decisions

Significant technical decisions are recorded as ADRs in `docs/adr/`. **Read the relevant ADR before proposing changes to persistence, testing, or infrastructure** — it captures the options that were considered and the reasons for the choice.

| ADR | Decision |
|-----|----------|
| [001](docs/adr/001-backend-language.md) | Backend language: FastAPI (Python) |
| [002](docs/adr/002-persistence-layer.md) | Persistence: PostgreSQL + SQLAlchemy async + Alembic; `DATABASE_URL` is the only env diff |
| [003](docs/adr/003-testing-strategy.md) | Testing: unit (no Docker, InMemoryRepository) / integration / e2e (testcontainers); repository pattern as the seam |

## Architecture

### Monorepo layout
- `apps/` — application code. Currently: `backend/`. Frontend to be added.
- `infra/k8s/` — Kustomize manifests. `base/` has the canonical resource definitions; `overlays/local/` patches for local kind dev (image tags, replica counts).
- `observability/` — Prometheus alerting rules (`prometheus/rules/`) and Grafana dashboard JSON (`grafana/dashboards/`), provisioned automatically into the cluster.
- `testing/performance/` — k6 scripts. `testing/chaos/` — LitmusChaos experiment manifests.
- `scripts/` — `setup.sh` (kind + Helm bootstrap) and `teardown.sh`.

### Backend (`apps/backend/`)
FastAPI 0.111+ on Python 3.11. Entry point: `app/main.py`.
- `app/core/config.py` — pydantic-settings; reads all config from env vars or `.env` file.
- `app/api/v1/` — versioned route modules, included with prefix `/api/v1`.
- Prometheus metrics auto-instrumented via `prometheus-fastapi-instrumentator`; exposed at `GET /metrics`.
- Health endpoint: `GET /api/v1/health` — used by k8s liveness and readiness probes.
- OpenAPI docs available at `/docs` when running locally.

### Kubernetes strategy
Kustomize-based. Base manifests declare resources without environment-specific values. Overlays patch image tags and environment-specific config. `skaffold dev` is the primary local dev loop — it builds the Docker image into the kind cluster and re-deploys on source changes.

### Observability
`kube-prometheus-stack` (Helm) installs Prometheus + Grafana + kube-state-metrics as a single release in the `monitoring` namespace. Backend pods are scraped via `prometheus.io/scrape` pod annotations. Custom dashboards added to `observability/grafana/dashboards/` are auto-provisioned.

### Local cluster name
The kind cluster is named `integrador`. The kubectl context is `kind-integrador`.

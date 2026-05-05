# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [1.0.0] — 2026-05-05

First production release. Covers the full local-dev stack: a FastAPI marketplace backend, a Next.js storefront frontend, a Docker-based observability stack (Prometheus + Grafana + Loki), and a k6 performance test suite.

### Added

#### Backend (`apps/backend/`)
- FastAPI marketplace API with item CRUD, search by title/category, and a hold/confirm purchase flow
- PostgreSQL persistence via SQLAlchemy async + Alembic migrations; `DATABASE_URL` is the only environment difference between local and production
- Anonymous auth stub: `seller_id` assigned server-side (removed from POST body); buyer identified via `caller_id` query param on hold endpoints
- CORS middleware allowing `localhost:3000` for local frontend development
- Prometheus metrics auto-instrumented via `prometheus-fastapi-instrumentator` at `GET /metrics`
- Item lifecycle counters (`item_events_total`) with `event` and `actor` labels for created, deleted, on_hold, hold_released, confirmed, and sold events
- Structured logging: JSON to rotating file (Loki-ready) + human-readable coloured output to console via `python-json-logger` and a custom `HumanFormatter`

#### Frontend (`apps/frontend/`)
- Next.js 14 App Router storefront with home (search + browse), item detail, and post-item pages
- TanStack Query for all server state; nuqs for URL-synced search parameters (query, category, page)
- Typed API client in `src/lib/api.ts` targeting `NEXT_PUBLIC_API_URL`
- Vitest + React Testing Library unit tests; MSW for API mocking in tests

#### CI (`/github/workflows/`)
- Backend CI: lint (ruff), unit tests with 80% coverage gate, integration and e2e tests via testcontainers
- Coverage percentage posted as a PR comment on every pull request

#### Observability (`observability/`)
- Local Docker Compose stack: Prometheus (`:9090`), Grafana (`:3001`), Loki (`:3100`), Promtail
- Prometheus scrapes the backend at `host.docker.internal:8000`; Remote Write receiver enabled for k6
- Grafana auto-provisions two dashboards and two datasources (Prometheus + Loki) on startup
- **Item Lifecycle Events** dashboard: stat panels for created/deleted/on_hold/sold counts + event rate time series
- Promtail scrapes `apps/backend/logs/app.log`, promotes `level` and `event` fields as Loki labels
- `make obs-up` / `make obs-down` targets; `PROMETHEUS_URL` env var skips local Prometheus when an external instance is available

#### Performance testing (`testing/performance/`)
- k6 smoke (1 VU, 1 min), load (20 VUs, ~5 min), and stress (500 → 1 500 VUs, ~10 min) scripts
- Shared helper library covering all API endpoints with named tags for per-endpoint metrics
- Results pushed to Prometheus via Remote Write; p50/p95/p99 percentiles enabled
- **k6 Performance Tests** Grafana dashboard: live VU count, request rate, p95 latency, error rate, per-endpoint throughput and latency trends
- `make perf-smoke` / `perf-load` / `perf-stress` targets

#### Developer experience
- `make setup` / `make teardown` scripts start and stop the full local stack (PostgreSQL, observability, backend, frontend) with health-check loops and PID tracking for clean teardown
- ADRs documenting decisions on language, persistence, testing strategy, and frontend stack (`docs/adr/`)
- Branching model: `feature/{issue_id}-{name}` off `develop`; PRs target `develop`; `develop` merges to `main` for releases

### Infrastructure
- Kustomize manifests for Kubernetes deployment (`infra/k8s/base/` + `overlays/local/`)
- Skaffold dev loop (`make dev`) for live rebuild and redeploy into a local kind cluster

---

[1.0.0]: https://github.com/Fgeorgescu/olly-and-testing/releases/tag/v1.0.0

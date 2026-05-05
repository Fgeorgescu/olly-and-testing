# Backend

FastAPI service providing the core REST API for the Integrador marketplace.

## Stack

| Library | Purpose |
|---------|---------|
| Python 3.11 | Runtime |
| FastAPI 0.111+ | REST framework, OpenAPI docs |
| SQLAlchemy 2 async + asyncpg | PostgreSQL ORM |
| Alembic | Database migrations |
| pydantic-settings | Environment-based configuration |
| prometheus-fastapi-instrumentator | Automatic HTTP metrics |
| prometheus-client | Custom lifecycle counters |
| python-json-logger | Structured JSON logging |
| uv | Dependency management |

## Local Development

```bash
# From the repo root — starts everything
make setup

# Or run the backend alone (PostgreSQL must be up)
make db-up
make backend-run   # hot-reload on http://localhost:8000
```

Interactive docs: http://localhost:8000/docs

## Environment Variables

Loaded from environment or a `.env` file in `apps/backend/`.

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://...` | PostgreSQL connection string |
| `APP_NAME` | `integrador-backend` | Application name |
| `VERSION` | `0.1.0` | API version |
| `ENVIRONMENT` | `development` | Runtime environment |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/health` | Liveness/readiness check |
| `GET` | `/metrics` | Prometheus metrics scrape endpoint |
| `POST` | `/api/v1/items` | Create a listing |
| `GET` | `/api/v1/items` | Search/list items |
| `GET` | `/api/v1/items/{id}` | Get item detail |
| `PUT` | `/api/v1/items/{id}` | Update item |
| `DELETE` | `/api/v1/items/{id}` | Delete item |
| `POST` | `/api/v1/items/{id}/hold` | Place a purchase hold |
| `DELETE` | `/api/v1/items/{id}/hold` | Release a hold |
| `POST` | `/api/v1/items/{id}/confirm` | Confirm purchase (buyer or seller) |

## Testing

Tests are split into three tiers (see [ADR-003](../../docs/adr/003-testing-strategy.md)):

```bash
make backend-test-unit   # unit — no Docker, in-memory repo, fast
make backend-test-int    # integration — requires Docker (testcontainers)
make backend-test-e2e    # e2e — requires Docker (testcontainers), full HTTP stack
make backend-test        # all tiers
```

CI enforces an 80% coverage gate on the unit tier and posts a coverage comment on every PR.

## Observability

The backend emits two kinds of signals:

**Metrics** (`/metrics` — Prometheus format):
- HTTP request metrics auto-instrumented by `prometheus-fastapi-instrumentator`
- `item_events_total{event, actor}` — lifecycle counter incremented on every state transition (created, deleted, on_hold, hold_released, confirmed, sold)

**Logs** (`logs/app.log` — JSON, scraped by Promtail → Loki):
- Console output: human-readable `HH:MM:SS  LEVEL  event  item_id  actor=…`
- File output: structured JSON with `timestamp`, `level`, `logger`, `event`, `item_id`, `actor`

See [observability/README.md](../../observability/README.md) for the Grafana dashboard.

## Spec-Driven Development

All features start with a spec file in [`specs/features/`](specs/features/) following the template in [`specs/_template.md`](specs/_template.md). No implementation PR is opened without a spec in `Approved` status.

## Linting

```bash
make backend-lint          # ruff check + format check
cd apps/backend && uv run ruff format .   # auto-format
```

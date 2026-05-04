# Backend

FastAPI service providing the core REST API for the Integrador platform.

## Stack

- **Python 3.11**
- **FastAPI 0.111+** — REST framework with automatic OpenAPI docs
- **pydantic-settings** — environment-based configuration
- **prometheus-fastapi-instrumentator** — automatic Prometheus metrics
- **uvicorn** — ASGI server

## Spec-Driven Development

All features are defined in a spec file before any code is written. Specs live in [`specs/features/`](specs/features/) and follow the template in [`specs/_template.md`](specs/_template.md). See [`specs/README.md`](specs/README.md) for the full workflow and lifecycle.

**Rule**: no implementation PR is opened without a spec in `Approved` status.

## Local Development

```bash
# Install dependencies (from this directory)
pip install -e ".[dev]"

# Run with hot-reload
uvicorn app.main:app --reload --port 8000
```

API is available at `http://localhost:8000`.
Interactive docs at `http://localhost:8000/docs`.

## Environment Variables

All config is loaded from environment variables or a `.env` file in this directory.

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | `integrador-backend` | Application name |
| `VERSION` | `0.1.0` | API version |
| `ENVIRONMENT` | `development` | Runtime environment |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/health` | Liveness/readiness check |
| `GET` | `/metrics` | Prometheus metrics scrape endpoint |
| `GET` | `/docs` | Swagger UI (development only) |

## Testing

```bash
# Run all tests
pytest

# Run a single file
pytest tests/test_health.py

# Run with output
pytest -s
```

## Linting

```bash
ruff check .          # lint
ruff format --check . # format check
ruff format .         # auto-format
```

## Docker

```bash
# Build image
docker build -t integrador/backend:latest .

# Run container
docker run -p 8000:8000 integrador/backend:latest
```

## Deployment

For Kubernetes deployment, see [infra/k8s/README.md](../../infra/k8s/README.md).
The backend is deployed as a `Deployment` with liveness and readiness probes pointing at `/api/v1/health`, and Prometheus scraping enabled via pod annotations.

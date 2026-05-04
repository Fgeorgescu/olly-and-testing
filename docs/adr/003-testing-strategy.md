# ADR 003: Testing Strategy — Three-Tier Split with Repository Pattern

Date: 2026-05-04
Status: Accepted

## Context

The backend needs a testing approach that supports fast local iteration (no external services) while also validating real database behaviour and the full HTTP stack. The choice of persistence layer (PostgreSQL, ADR-002) and the pluggable `SearchBackend` protocol already established a pattern of depending on interfaces rather than concrete implementations. The testing strategy extends this pattern to the entire service layer.

## Decision

Tests are split into three tiers, each with a distinct scope and execution requirement:

| Tier | Directory | Requires Docker? | What it tests |
|------|-----------|-----------------|---------------|
| Unit | `tests/unit/` | No | Business logic and service layer against an `InMemoryRepository` |
| Integration | `tests/integration/` | Yes | SQLAlchemy repository against a real PostgreSQL (via `testcontainers`) |
| E2E | `tests/e2e/` | Yes | Full HTTP request → SQLAlchemy → PostgreSQL cycle via FastAPI `TestClient` |

### Repository pattern as the seam

All service-layer code depends on a `Repository` protocol (e.g., `ItemRepository`), not on SQLAlchemy directly. Two concrete implementations exist:

- `InMemoryItemRepository` — a plain Python dict; used in unit tests, requires no imports beyond stdlib
- `PostgresItemRepository` — SQLAlchemy async implementation; used in integration and E2E tests

Unit tests never touch SQLAlchemy or a network connection. Integration and E2E tests use `testcontainers-python` to spin up a real PostgreSQL container automatically; they are skipped if Docker is unavailable.

### pytest markers

```
pytest tests/unit/                        # no Docker needed, always fast
pytest tests/integration/ tests/e2e/     # requires Docker
pytest                                    # all tiers
pytest -m unit                           # explicit unit-only run
```

Markers (`unit`, `integration`, `e2e`) are declared in `pyproject.toml` under `[tool.pytest.ini_options]`.

## Consequences

- Positive: unit tests run in milliseconds with only Python and pytest — no setup required; the repository interface enforces a clean separation between business logic and infrastructure; the same pattern applies to `SearchBackend` and any future external dependency.
- Negative: maintaining two repository implementations (in-memory and Postgres) adds a small amount of code; the in-memory fake must be kept in sync with the interface as it evolves.
- Neutral: `testcontainers-python` is added as a dev dependency; it manages the PostgreSQL container lifecycle automatically so integration and E2E tests need no manual setup beyond having Docker running.

# ADR 002: Persistence Layer — PostgreSQL + SQLAlchemy (async) + Alembic

Date: 2026-05-04
Status: Accepted

## Context

The ecommerce backend needs a persistence layer for items, holds, and future entities. The search spec already plans a `FullTextSearchBackend` using PostgreSQL `tsvector`, so the choice of database has a direct impact on the search roadmap. The project runs in three distinct execution contexts — local development, local Kubernetes (kind), and production/staging — each with different infrastructure constraints.

Options considered:
- **PostgreSQL** — relational, supports `tsvector` full-text search, production-grade
- **SQLite** — zero-infra for local dev, but not viable in k8s and has dialect differences that can hide bugs
- **MongoDB** — document store, flexible schema, but misaligned with the full-text search roadmap and relational hold/user model

## Decision

PostgreSQL as the database, SQLAlchemy (async, via `asyncpg`) as the ORM, and Alembic for schema migrations.

Environment differentiation is handled exclusively through the `DATABASE_URL` environment variable — no code changes between environments:

| Context | How PostgreSQL is provided |
|---------|---------------------------|
| Local dev (daily iteration) | `docker compose up db` — single command, no k8s needed |
| Local k8s (`make dev`) | PostgreSQL `StatefulSet` in the kind cluster; `DATABASE_URL` from a k8s `Secret` |
| Staging / Production | PostgreSQL `StatefulSet` or managed service (RDS, Cloud SQL); `DATABASE_URL` from a k8s `Secret` |

Alembic migrations run as an **init container** in k8s (before the backend pod starts) and manually via `alembic upgrade head` in local dev.

## Consequences

- Positive: single database dialect across all environments eliminates dialect-mismatch bugs; `tsvector` full-text search is available when needed without adding a new service; `DATABASE_URL` abstraction keeps environment switching trivial.
- Negative: local dev requires Docker running for the database; adds a stateful service to the k8s manifests.
- Neutral: `docker compose` is added to the repo for local dev convenience; it is not used in k8s or CI.

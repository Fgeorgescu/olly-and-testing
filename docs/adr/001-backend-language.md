# ADR 001: Backend Language — FastAPI (Python)

Date: 2026-05-04
Status: Accepted

## Context
Needed a backend API framework for initial scaffolding. Options: FastAPI (Python), Go + chi.

## Decision
FastAPI. Faster to prototype, strong async support, automatic OpenAPI docs at `/docs`, and Pydantic for request/response validation.

## Consequences
- Positive: rapid development, large ecosystem, native Prometheus integration via `prometheus-fastapi-instrumentator`.
- Negative: higher memory footprint than Go; may revisit if resource constraints become significant in the local cluster.

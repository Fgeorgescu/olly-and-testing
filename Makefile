.PHONY: help setup teardown dev k8s-setup k8s-teardown backend-install backend-run backend-test backend-test-unit backend-test-int backend-test-e2e backend-lint db-up db-down obs-up obs-down perf-smoke perf-load perf-stress

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Start all local services (DB, observability, backend, frontend)
	./scripts/setup.sh

teardown: ## Stop all local services
	./scripts/teardown.sh

k8s-setup: ## Create kind cluster + install Prometheus & ArgoCD via Helm (for Kubernetes practice)
	./scripts/k8s-setup.sh

k8s-teardown: ## Destroy the kind cluster
	./scripts/k8s-teardown.sh

dev: ## Start Skaffold watch loop (build + deploy on change)
	skaffold dev --port-forward

backend-install: ## Create .venv and sync all dependencies via uv
	cd apps/backend && uv sync --extra dev

backend-run: ## Run backend locally with hot-reload
	cd apps/backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

backend-test: ## Run all backend tests (requires Docker for integration/e2e)
	cd apps/backend && uv run pytest

backend-test-unit: ## Run unit tests only (no Docker required)
	cd apps/backend && uv run pytest -m unit

backend-test-int: ## Run integration tests (requires Docker)
	cd apps/backend && uv run pytest -m integration

backend-test-e2e: ## Run e2e tests (requires Docker)
	cd apps/backend && uv run pytest -m e2e

backend-lint: ## Lint and format-check backend
	cd apps/backend && uv run ruff check . && uv run ruff format --check .

db-up: ## Start local PostgreSQL via docker compose
	cd apps/backend && docker compose up -d db

db-down: ## Stop local PostgreSQL
	cd apps/backend && docker compose down

obs-up: ## Start observability stack. Set PROMETHEUS_URL to use an existing Prometheus and start only Grafana.
	@if [ -z "$(PROMETHEUS_URL)" ]; then \
		echo "Starting Prometheus + Grafana (Prometheus on :9090, Grafana on :3001)..."; \
		cd observability && docker-compose --profile local-prometheus up -d; \
	else \
		echo "PROMETHEUS_URL=$(PROMETHEUS_URL) - starting Grafana only (:3001)..."; \
		cd observability && docker-compose up -d grafana; \
	fi

obs-down: ## Stop observability stack
	cd observability && docker-compose --profile local-prometheus down

perf-smoke: ## Run smoke test and push results to Prometheus (requires k6 + services running)
	K6_PROMETHEUS_RW_SERVER_URL=http://localhost:9090/api/v1/write \
	K6_PROMETHEUS_RW_TREND_STATS="p(50),p(95),p(99)" \
	k6 run --out experimental-prometheus-rw testing/performance/smoke.js

perf-load: ## Run load test and push results to Prometheus
	K6_PROMETHEUS_RW_SERVER_URL=http://localhost:9090/api/v1/write \
	K6_PROMETHEUS_RW_TREND_STATS="p(50),p(95),p(99)" \
	k6 run --out experimental-prometheus-rw testing/performance/load.js

perf-stress: ## Run stress test and push results to Prometheus
	K6_PROMETHEUS_RW_SERVER_URL=http://localhost:9090/api/v1/write \
	K6_PROMETHEUS_RW_TREND_STATS="p(50),p(95),p(99)" \
	k6 run --out experimental-prometheus-rw testing/performance/stress.js

.PHONY: help setup teardown dev backend-install backend-run backend-test backend-test-unit backend-test-int backend-test-e2e backend-lint db-up db-down obs-up obs-down

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Bootstrap local kind cluster and install observability stack
	./scripts/setup.sh

teardown: ## Destroy local kind cluster
	./scripts/teardown.sh

dev: ## Start Skaffold watch loop (build + deploy on change)
	skaffold dev --port-forward

backend-install: ## Create .venv and sync all dependencies via uv
	cd apps/backend && uv sync --extra dev

backend-run: ## Run backend locally with hot-reload
	cd apps/backend && uv run uvicorn app.main:app --reload --port 8000

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

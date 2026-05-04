.PHONY: help setup teardown dev backend-install backend-run backend-test backend-lint

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Bootstrap local kind cluster and install observability stack
	./scripts/setup.sh

teardown: ## Destroy local kind cluster
	./scripts/teardown.sh

dev: ## Start Skaffold watch loop (build + deploy on change)
	skaffold dev --port-forward

backend-install: ## Install backend dependencies (dev mode)
	cd apps/backend && pip install -e ".[dev]"

backend-run: ## Run backend locally with hot-reload
	cd apps/backend && uvicorn app.main:app --reload --port 8000

backend-test: ## Run backend tests
	cd apps/backend && pytest

backend-lint: ## Lint and format-check backend
	cd apps/backend && ruff check . && ruff format --check .

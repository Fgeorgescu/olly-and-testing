# Integrador

A monorepo that integrates multiple software development projects under a shared local Kubernetes environment with full observability, performance testing, and chaos engineering.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      Local kind cluster                      │
│                                                              │
│   ┌────────────┐   HTTP    ┌────────────┐                   │
│   │  Frontend  │ ────────▶ │  Backend   │                   │
│   │  (Next.js) │           │  (FastAPI) │                   │
│   └────────────┘           └─────┬──────┘                   │
│                                  │ /metrics                  │
│                           ┌──────▼──────────────────────┐   │
│                           │  Prometheus  │    Grafana    │   │
│                           └─────────────┴───────────────┘   │
│                                                              │
│   ┌─────────────────┐     ┌────────────────────────────┐    │
│   │   k6 (perf)     │     │  LitmusChaos (chaos)       │    │
│   └─────────────────┘     └────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

## Prerequisites

| Tool | Purpose | Install |
|------|---------|---------|
| [Docker](https://docs.docker.com/get-docker/) | Container runtime | Required |
| [kind](https://kind.sigs.k8s.io/docs/user/quick-start/) | Local Kubernetes cluster | `brew install kind` |
| [kubectl](https://kubernetes.io/docs/tasks/tools/) | Kubernetes CLI | `brew install kubectl` |
| [Helm](https://helm.sh/docs/intro/install/) | Package manager for k8s | `brew install helm` |
| [Skaffold](https://skaffold.dev/docs/install/) | Local dev loop | `brew install skaffold` |
| Python 3.11+ | Backend runtime | `brew install python@3.11` |

## Quick Start

```bash
# 1. Bootstrap the local cluster and install the observability stack
make setup

# 2. Start the dev loop — builds images and deploys to kind on file change
make dev

# 3. Access services
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80        # Grafana
kubectl port-forward -n monitoring svc/monitoring-kube-prometheus-prometheus 9090:9090  # Prometheus
kubectl port-forward svc/backend 8000:8000                               # Backend API
```

## Components

| Component | Description | README |
|-----------|-------------|--------|
| Backend | FastAPI REST API, metrics, health checks | [apps/backend/README.md](apps/backend/README.md) |
| Frontend | Web UI (Next.js) | [apps/frontend/README.md](apps/frontend/README.md) |
| Kubernetes | Kustomize manifests + Skaffold dev loop | [infra/k8s/README.md](infra/k8s/README.md) |
| Observability | Prometheus + Grafana dashboards and alerts | [observability/README.md](observability/README.md) |
| Performance testing | k6 load and smoke tests | [testing/performance/README.md](testing/performance/README.md) |
| Chaos testing | LitmusChaos experiments | [testing/chaos/README.md](testing/chaos/README.md) |

## Repository Structure

```
integrador/
├── apps/
│   ├── backend/        # FastAPI service
│   └── frontend/       # Next.js app (planned)
├── infra/
│   ├── k8s/            # Kustomize manifests
│   └── helm/           # Third-party Helm values
├── observability/
│   ├── prometheus/     # Alerting rules
│   └── grafana/        # Dashboard JSON + provisioning
├── testing/
│   ├── performance/    # k6 scripts
│   └── chaos/          # LitmusChaos experiments
├── scripts/            # setup.sh / teardown.sh
├── docs/adr/           # Architecture Decision Records
├── skaffold.yaml
└── Makefile
```

## Makefile Reference

```bash
make setup          # Create kind cluster + install observability stack
make dev            # Skaffold watch loop (build + deploy on change)
make teardown       # Destroy the kind cluster
make backend-test   # Run backend tests
make backend-lint   # Lint backend code
```

## Architecture Decisions

Design decisions are documented as ADRs in [`docs/adr/`](docs/adr/).

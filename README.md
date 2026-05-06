# Integrador

A full-stack marketplace monorepo with a FastAPI backend, Next.js frontend, and a local observability stack (Prometheus + Loki + Grafana).

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Local dev environment                    │
│                                                                 │
│   ┌────────────┐   HTTP    ┌─────────────┐   SQL   ┌────────┐  │
│   │  Frontend  │ ────────▶ │   Backend   │ ──────▶ │  PG   │  │
│   │  (Next.js) │           │  (FastAPI)  │         │  DB   │  │
│   │  :3000     │           │  :8000      │         └────────┘  │
│   └────────────┘           └──────┬──────┘                     │
│                                   │ /metrics + logs/app.log    │
│                 ┌─────────────────┼──────────────────────┐     │
│                 │   Observability │ stack                 │     │
│                 │                 ▼                       │     │
│                 │  ┌──────────┐  ┌───────┐  ┌─────────┐  │     │
│                 │  │Prometheus│  │ Loki  │  │ Grafana │  │     │
│                 │  │  :9090   │  │ :3100 │  │  :3001  │  │     │
│                 │  └──────────┘  └───┬───┘  └─────────┘  │     │
│                 │                    │                     │     │
│                 │             ┌──────┘                     │     │
│                 │         ┌───▼────┐                       │     │
│                 │         │Promtail│ (scrapes logs/)       │     │
│                 │         └────────┘                       │     │
│                 └─────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

## Prerequisites

| Tool | Purpose |
|------|---------|
| [Docker](https://docs.docker.com/get-docker/) + docker-compose | Container runtime |
| [Python 3.11+](https://www.python.org/) + [uv](https://github.com/astral-sh/uv) | Backend runtime |
| [Node.js 18+](https://nodejs.org/) | Frontend runtime |

## Quick Start

```bash
# Start everything (DB, observability, backend, frontend)
make setup

# Stop everything
make teardown
```

That's it. `make setup` installs dependencies, starts all services, waits for health checks, and prints the URLs.

### Kubernetes environment (for cluster practice)

A separate make target spins up a local [kind](https://kind.sigs.k8s.io/) cluster with Prometheus, Grafana, and ArgoCD — independent from the Docker Compose setup above:

```bash
make k8s-setup      # Create kind cluster + install monitoring + ArgoCD
make k8s-teardown   # Destroy the kind cluster
```

Expose services after setup (each in its own terminal):

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:80
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80
kubectl port-forward -n monitoring svc/monitoring-kube-prometheus-prometheus 9090:9090
```

## URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | — |
| Backend API | http://localhost:8000/docs | — |
| Grafana | http://localhost:3001 | admin / admin |
| Prometheus | http://localhost:9090 | — |
| Loki | http://localhost:3100 | — |

## Components

| Component | Description | README |
|-----------|-------------|--------|
| Backend | FastAPI REST API with Prometheus metrics and structured logging | [apps/backend/README.md](apps/backend/README.md) |
| Frontend | Next.js marketplace UI | [apps/frontend/README.md](apps/frontend/README.md) |
| Observability | Prometheus + Loki + Grafana local stack | [observability/README.md](observability/README.md) |

## Repository Structure

```
integrador/
├── apps/
│   ├── backend/        # FastAPI service
│   └── frontend/       # Next.js app
├── observability/
│   ├── docker-compose.yml          # Prometheus, Loki, Promtail, Grafana
│   ├── prometheus.yml              # Scrape config
│   ├── loki/                       # Loki config
│   ├── promtail/                   # Promtail config
│   └── grafana/
│       ├── dashboards/             # Dashboard JSON files
│       └── provisioning/           # Auto-provisioned datasources + dashboards
├── infra/k8s/          # Kustomize manifests (Kubernetes deployment)
├── scripts/
│   ├── setup.sh        # Start all local services
│   └── teardown.sh     # Stop all local services
├── docs/adr/           # Architecture Decision Records
└── Makefile
```

## Makefile Reference

```bash
# Docker Compose environment
make setup              # Start all local services (DB, observability, backend, frontend)
make teardown           # Stop all local services

# Kubernetes environment
make k8s-setup          # Create kind cluster + install Prometheus & ArgoCD via Helm
make k8s-teardown       # Destroy the kind cluster

make backend-install    # Install backend Python dependencies
make backend-run        # Run backend with hot-reload (port 8000)
make backend-test       # Run all backend tests
make backend-test-unit  # Run unit tests only (no Docker required)
make backend-lint       # Lint and format-check backend

make db-up              # Start PostgreSQL only
make db-down            # Stop PostgreSQL

make obs-up             # Start observability stack only
make obs-down           # Stop observability stack
```

Set `PROMETHEUS_URL` to use an existing Prometheus instance — only Grafana and Loki will start:

```bash
PROMETHEUS_URL=http://my-prometheus:9090 make obs-up
```

## Kubernetes & GitOps Concepts

### Core Kubernetes objects

| Object | Description |
|--------|-------------|
| **Pod** | Smallest deployable unit — one or more containers sharing network and storage |
| **Deployment** | Manages a ReplicaSet; handles rollouts, rollbacks, and desired replica count |
| **Service** | Stable network endpoint (ClusterIP, NodePort, LoadBalancer) for a set of pods |
| **Namespace** | Virtual cluster for isolating resources within a cluster |
| **ConfigMap / Secret** | Externalized configuration and sensitive data injected into pods |
| **HorizontalPodAutoscaler** | Scales replica count based on CPU, memory, or custom metrics |
| **ResourceQuota** | Caps total resource consumption or object count within a namespace |
| **LimitRange** | Sets default and maximum resource limits per container in a namespace |

### CPU resource units

Kubernetes measures CPU in **millicores** (`m`): 1000m = 1 full CPU core. A limit of `200m` means the container may use at most 20% of one core per scheduling period, enforced by the Linux kernel's CFS scheduler via cgroups.

- `requests.cpu` — minimum guaranteed; used by the scheduler to decide which node fits the pod
- `limits.cpu` — hard cap; the process is throttled (not killed) when exceeded

### Scaling strategies

| Strategy | What scales | Best for |
|----------|------------|---------|
| **HPA** (HorizontalPodAutoscaler) | Number of pod replicas | Stateless services with variable load |
| **VPA** (VerticalPodAutoscaler) | CPU/memory requests of existing pods | Stateful apps that can't run multiple replicas |
| **Cluster Autoscaler** | Number of nodes | Cloud clusters that need to grow/shrink the node pool |
| **KEDA** | Replicas driven by external events | Queue-based or event-driven workloads (Kafka, SQS, cron) |

### GitOps with ArgoCD

ArgoCD runs inside the cluster and continuously syncs its state to match a Git repository. The Git repo is the single source of truth — no manual `kubectl apply` in production.

```
Developer pushes YAML → ArgoCD detects change → applies diff to cluster
```

- CI owns the image (build + push to registry, update image tag in Git)
- ArgoCD owns the deployment (watches Git, applies changes automatically)
- The ArgoCD UI shows live vs desired state, sync status, and resource health

## Architecture Decisions

Design decisions are documented as ADRs in [`docs/adr/`](docs/adr/).

| ADR | Decision |
|-----|----------|
| [001](docs/adr/001-backend-language.md) | Backend language: FastAPI (Python) |
| [002](docs/adr/002-persistence-layer.md) | Persistence: PostgreSQL + SQLAlchemy async + Alembic |
| [003](docs/adr/003-testing-strategy.md) | Testing: unit / integration / e2e tiers with repository pattern |

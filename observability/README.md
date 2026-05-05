# Observability

Local observability stack for the Integrador platform, running entirely in Docker Compose. No Kubernetes required.

## Components

| Component | Purpose | Port |
|-----------|---------|------|
| Prometheus | Metrics collection and querying | 9090 |
| Loki | Log aggregation | 3100 |
| Promtail | Log shipper (scrapes `apps/backend/logs/app.log`) | — |
| Grafana | Dashboards and visualization | 3001 |

## Quick Start

```bash
# Start the full stack (Prometheus + Loki + Promtail + Grafana)
make obs-up

# Stop
make obs-down
```

Grafana is available at **http://localhost:3001** with credentials `admin / admin`.

## Using an Existing Prometheus

If you already have a Prometheus instance, set `PROMETHEUS_URL` — only Grafana and Loki will start:

```bash
PROMETHEUS_URL=http://my-prometheus:9090 make obs-up
```

## How Metrics Are Scraped

Prometheus scrapes the backend's `/metrics` endpoint directly on the host:

```yaml
# observability/prometheus.yml
scrape_configs:
  - job_name: "integrador-backend"
    static_configs:
      - targets: ["host.docker.internal:8000"]
```

The backend must be started with `--host 0.0.0.0` (the default via `make backend-run`) so it is reachable from Docker containers via the bridge gateway.

## How Logs Are Shipped

The backend writes structured JSON logs to `apps/backend/logs/app.log`. Promtail mounts that directory and ships each line to Loki. The JSON fields `level` and `event` are promoted to Loki labels for efficient filtering.

```
backend → logs/app.log → Promtail → Loki → Grafana
```

## Dashboards

Dashboards are provisioned automatically from `grafana/dashboards/`. No manual import needed.

| Dashboard | UID | Description |
|-----------|-----|-------------|
| Item Lifecycle Events | `integrador-item-lifecycle` | Prometheus counters (created, deleted, on_hold, sold) + event rate time series + Loki log panel |

## Adding a Dashboard

1. Build it in the Grafana UI
2. Export as JSON (`Share → Export → Save to file`)
3. Save to `grafana/dashboards/<name>.json`
4. Restart Grafana (`docker restart observability_grafana_1`) — it reloads every 30 s automatically

## Datasources

Provisioned from `grafana/provisioning/datasources/`:

| Datasource | UID | URL |
|------------|-----|-----|
| Prometheus | `integrador-prometheus` | `${PROMETHEUS_URL}` (default: `http://prometheus:9090`) |
| Loki | `integrador-loki` | `http://loki:3100` |

Dashboard JSON files must reference these UIDs exactly.

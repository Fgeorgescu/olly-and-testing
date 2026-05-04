# Observability

Metrics and dashboards powered by [kube-prometheus-stack](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack), which bundles Prometheus, Grafana, Alertmanager, and kube-state-metrics into a single Helm release.

## Installed Components

| Component | Purpose | Default port |
|-----------|---------|-------------|
| Prometheus | Metrics storage and querying | 9090 |
| Grafana | Dashboards and visualization | 3000 |
| Alertmanager | Alert routing | 9093 |
| kube-state-metrics | Kubernetes object metrics | — |

Installed in the `monitoring` namespace via `make setup`.

## Accessing Locally

```bash
# Grafana (admin / admin)
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80

# Prometheus
kubectl port-forward -n monitoring svc/monitoring-kube-prometheus-prometheus 9090:9090

# Alertmanager
kubectl port-forward -n monitoring svc/monitoring-kube-prometheus-alertmanager 9093:9093
```

## How Metrics Are Scraped

Application pods are scraped automatically via pod annotations:

```yaml
annotations:
  prometheus.io/scrape: "true"
  prometheus.io/path: "/metrics"
  prometheus.io/port: "8000"
```

The backend exposes these annotations. Any new service that adds them will be picked up without additional Prometheus config.

## Adding a Custom Dashboard

1. Build and export the dashboard JSON from the Grafana UI
2. Save it to `observability/grafana/dashboards/<name>.json`
3. Ensure `observability/grafana/provisioning/` contains a datasource/dashboard provisioning config pointing at that directory
4. The provisioning config is mounted into the Grafana pod via a ConfigMap (to be wired up in `infra/k8s`)

## Adding Alert Rules

1. Create a `PrometheusRule` manifest in `observability/prometheus/rules/<name>.yaml`
2. Apply it: `kubectl apply -f observability/prometheus/rules/<name>.yaml`

Example rule structure:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: backend-alerts
  namespace: monitoring
spec:
  groups:
  - name: backend
    rules:
    - alert: BackendDown
      expr: up{job="backend"} == 0
      for: 1m
      annotations:
        summary: "Backend is down"
```

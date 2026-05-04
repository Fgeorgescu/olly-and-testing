# Performance Testing

Load and smoke tests using [k6](https://grafana.com/docs/k6/latest/).

## Prerequisites

```bash
# macOS
brew install k6

# Linux
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt update && sudo apt install k6
```

## Running Tests

Scripts live in this directory. Port-forward the target service before running:

```bash
kubectl port-forward svc/backend 8000:8000

# Run a script
k6 run testing/performance/smoke.js

# Run with a specific number of VUs and duration
k6 run --vus 10 --duration 30s testing/performance/smoke.js
```

## Script Conventions

| File | Purpose |
|------|---------|
| `smoke.js` | Minimal load — verifies the system works under negligible traffic |
| `load.js` | Normal expected load |
| `stress.js` | Above-normal load to find the breaking point |

## Exporting Metrics to Prometheus

k6 can push metrics to Prometheus via the Remote Write protocol, making results visible in Grafana alongside application metrics:

```bash
K6_PROMETHEUS_RW_SERVER_URL=http://localhost:9090/api/v1/write \
  k6 run --out=experimental-prometheus-rw testing/performance/smoke.js
```

> Requires Prometheus Remote Write to be enabled. See the [observability README](../../observability/README.md) for access details.

# Performance Testing

Load, smoke, and stress tests using [k6](https://grafana.com/docs/k6/latest/). Results are pushed to Prometheus via Remote Write and visible in a dedicated Grafana dashboard alongside application metrics.

## Prerequisites

Install k6 on Ubuntu/WSL2:

```bash
sudo apt-get install -y gnupg
curl -fsSL https://dl.k6.io/key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/k6-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update && sudo apt-get install -y k6
```

Services must be running (`make setup`) before executing any test.

## Running Tests

```bash
make perf-smoke    # 1 VU, 1 min — sanity check
make perf-load     # 20 VUs, ~5 min — normal expected load
make perf-stress   # up to 150 VUs, ~10 min — find the breaking point
```

Results appear in Grafana at **http://localhost:3001** → "k6 Performance Tests" dashboard within seconds of the test starting.

## Test Scenarios

| Script | VUs | Duration | Purpose |
|--------|-----|----------|---------|
| `smoke.js` | 1 | 1m | Verifies all endpoints respond correctly under negligible load |
| `load.js` | 20 | ~5m | Simulates normal traffic mix (60% browse, 30% create, 10% hold flow) |
| `stress.js` | 50→150 | ~10m | Pushes beyond normal load to find the breaking point |

## Traffic Mix (load + stress)

| Scenario | Weight | Endpoints |
|----------|--------|-----------|
| Browse | 60% | `GET /items`, `GET /items/:id` |
| Create listing | 30% | `POST /items` |
| Purchase hold | 10% | `POST /items/:id/hold`, `POST /items/:id/confirm` |

## Thresholds

| Test | Metric | Threshold |
|------|--------|-----------|
| smoke | error rate | < 1% |
| smoke | p95 latency | < 500ms |
| load | error rate | < 2% |
| load | p95 latency | < 1s |
| stress | error rate | < 10% |
| stress | p95 latency | < 3s |

k6 exits with a non-zero code if any threshold is breached.

## How Results Reach Grafana

```
k6 → Prometheus Remote Write (port 9090) → Prometheus → Grafana
```

The `--web.enable-remote-write-receiver` flag is set on the local Prometheus container. k6 pushes metrics every 5 seconds during the test run.

Key metrics pushed:
- `k6_http_req_duration` — response time histogram (p50/p95/p99)
- `k6_http_reqs_total` — request counter
- `k6_http_req_failed_total` — failed request counter
- `k6_vus` — active virtual users
- `k6_iterations_total` — scenario iteration counter
- `k6_data_sent_total` / `k6_data_received_total` — bandwidth

All metrics carry a `name` label matching the endpoint tag set in the script (e.g. `GET /items`, `POST /items`).

## Custom BASE_URL

```bash
BASE_URL=http://staging.example.com k6 run \
  --out experimental-prometheus-rw \
  testing/performance/smoke.js
```

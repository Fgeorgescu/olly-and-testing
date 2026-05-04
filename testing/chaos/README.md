# Chaos Testing

Chaos experiments using [LitmusChaos](https://litmuschaos.io/), a Kubernetes-native chaos engineering platform.

## Installation

```bash
# Install LitmusChaos via Helm
helm repo add litmuschaos https://litmuschaos.github.io/litmus-helm/
helm repo update
helm install chaos litmuschaos/litmus \
  --namespace litmus \
  --create-namespace \
  --wait

# Access the Litmus dashboard
kubectl port-forward -n litmus svc/chaos-litmus-frontend-service 9091:9091
# Open http://localhost:9091 (default: admin / litmus)
```

## Available Experiment Types

| Experiment | What it does |
|-----------|-------------|
| `pod-delete` | Randomly kills one or more pods |
| `pod-cpu-hog` | Spikes CPU inside a pod |
| `pod-memory-hog` | Spikes memory inside a pod |
| `network-latency` | Injects latency into pod network |
| `network-loss` | Drops a percentage of packets |

## Running an Experiment

Experiments are defined as `ChaosEngine` manifests. Store them in this directory and apply:

```bash
kubectl apply -f testing/chaos/pod-delete-backend.yaml
kubectl get chaosresult -w   # watch the result
```

## Observing During a Chaos Run

1. Open Grafana at `http://localhost:3000` (see [observability README](../../observability/README.md))
2. Watch the backend's request rate, error rate, and latency panels
3. Verify that liveness/readiness probes restart affected pods and traffic recovers

## Steady-State Hypothesis

Before running chaos, define what "healthy" looks like:
- `GET /api/v1/health` returns 200 within 500ms
- Error rate below 1%
- Pod restarts within 30 seconds

Experiments should validate that the system returns to this state after the fault is injected.

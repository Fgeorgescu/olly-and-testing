# Kubernetes Infrastructure

Local Kubernetes setup using [kind](https://kind.sigs.k8s.io/) with manifests managed by [Kustomize](https://kustomize.io/) and a [Skaffold](https://skaffold.dev/) dev loop.

## Kustomize Structure

```
infra/k8s/
├── base/               # Canonical resource definitions (env-agnostic)
│   ├── backend/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   └── kustomization.yaml
└── overlays/
    └── local/          # Patches for local kind development
        └── kustomization.yaml
```

**Base** manifests declare the resource shape. **Overlays** apply environment-specific patches (image tags, replica counts, config values) without modifying the base.

## Dev Loop with Skaffold

`skaffold dev` is the primary workflow for local development. It:
1. Builds Docker images for all artifacts
2. Loads them into the kind cluster (no registry needed)
3. Applies the `overlays/local` manifests
4. Watches source files and re-builds/re-deploys on change

```bash
# Start the dev loop (run from repo root)
skaffold dev --port-forward
```

`--port-forward` automatically forwards service ports to localhost.

## Applying Manifests Manually

```bash
# Apply local overlay
kubectl apply -k infra/k8s/overlays/local

# Diff before applying
kubectl diff -k infra/k8s/overlays/local
```

## Adding a New Service

1. Create `infra/k8s/base/<service>/deployment.yaml` and `service.yaml`
2. Add the new resource paths to `infra/k8s/base/kustomization.yaml`
3. Add the image to the `build.artifacts` list in `skaffold.yaml`
4. If the service needs local-specific config, add a patch in `overlays/local/kustomization.yaml`

## Useful Commands

```bash
kubectl get pods                          # Check pod status
kubectl logs -f deployment/backend        # Tail backend logs
kubectl describe pod <pod-name>           # Debug a failing pod
kubectl get events --sort-by=.lastTimestamp  # Recent cluster events
```

## Cluster Management

```bash
make setup      # Create the kind cluster (named: integrador)
make teardown   # Destroy the kind cluster
```

The kind cluster context is `kind-integrador`.

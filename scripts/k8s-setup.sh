#!/bin/bash
set -euo pipefail

CLUSTER_NAME="integrador"

# ── kubectl ───────────────────────────────────────────────────────────────────
if ! command -v kubectl &> /dev/null; then
  echo "==> kubectl not found — installing"
  KUBECTL_VERSION=$(curl -fsSL https://dl.k8s.io/release/stable.txt)
  curl -fsSL "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl" \
    -o /tmp/kubectl
  sudo install -o root -g root -m 0755 /tmp/kubectl /usr/local/bin/kubectl
  echo "    kubectl ${KUBECTL_VERSION} installed"
fi

# ── kind cluster ──────────────────────────────────────────────────────────────
if kind get clusters 2>/dev/null | grep -q "^${CLUSTER_NAME}$"; then
  echo "==> kind cluster '${CLUSTER_NAME}' already exists — skipping creation"
else
  echo "==> Creating kind cluster: ${CLUSTER_NAME}"
  kind create cluster --name "$CLUSTER_NAME" --wait 60s
fi

# ── Helm repos ────────────────────────────────────────────────────────────────
echo "==> Adding Helm repos"
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update

# ── kube-prometheus-stack ─────────────────────────────────────────────────────
echo "==> Installing kube-prometheus-stack (Prometheus + Grafana)"
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set grafana.adminPassword=admin \
  --wait

# ── ArgoCD ────────────────────────────────────────────────────────────────────
echo "==> Installing ArgoCD"
helm upgrade --install argocd argo/argo-cd \
  --namespace argocd \
  --create-namespace \
  --set configs.params."server\.insecure"=true \
  --wait

echo ""
echo "┌──────────────────────────────────────────────────────────────────────────────┐"
echo "│  Kubernetes cluster ready: kind-integrador                                  │"
echo "├──────────────────────────────────────────────────────────────────────────────┤"
echo "│  Expose services (run each in a separate terminal):                          │"
echo "│                                                                              │"
echo "│  ArgoCD:     kubectl port-forward svc/argocd-server -n argocd 8080:80       │"
echo "│  Grafana:    kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80│"
echo "│  Prometheus: kubectl port-forward -n monitoring \\                            │"
echo "│              svc/monitoring-kube-prometheus-prometheus 9090:9090             │"
echo "├──────────────────────────────────────────────────────────────────────────────┤"
echo "│  ArgoCD admin password:                                                      │"
echo "│    kubectl get secret argocd-initial-admin-secret -n argocd \\               │"
echo "│      -o jsonpath='{.data.password}' | base64 -d && echo                     │"
echo "├──────────────────────────────────────────────────────────────────────────────┤"
echo "│  Tear down: make k8s-teardown                                                │"
echo "└──────────────────────────────────────────────────────────────────────────────┘"

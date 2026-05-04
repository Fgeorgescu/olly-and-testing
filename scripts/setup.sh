#!/bin/bash
set -euo pipefail

CLUSTER_NAME="integrador"

echo "==> Creating kind cluster: $CLUSTER_NAME"
kind create cluster --name "$CLUSTER_NAME" --wait 60s

echo "==> Adding Helm repos"
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

echo "==> Installing kube-prometheus-stack (Prometheus + Grafana)"
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set grafana.adminPassword=admin \
  --wait

echo ""
echo "Setup complete. To access:"
echo "  Grafana:    kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80"
echo "  Prometheus: kubectl port-forward -n monitoring svc/monitoring-kube-prometheus-prometheus 9090:9090"
echo ""
echo "Start the dev loop: make dev"

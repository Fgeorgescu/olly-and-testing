#!/bin/bash
set -euo pipefail

CLUSTER_NAME="integrador"

if ! kind get clusters 2>/dev/null | grep -q "^${CLUSTER_NAME}$"; then
  echo "==> Cluster '${CLUSTER_NAME}' not found — nothing to tear down."
  exit 0
fi

echo "==> Deleting kind cluster: ${CLUSTER_NAME}"
kind delete cluster --name "$CLUSTER_NAME"
echo "    Done."

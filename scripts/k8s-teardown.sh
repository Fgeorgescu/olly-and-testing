#!/bin/bash
set -euo pipefail

CLUSTER_NAME="integrador"

echo "==> Deleting kind cluster: ${CLUSTER_NAME}"
kind delete cluster --name "$CLUSTER_NAME"
echo "    Done."

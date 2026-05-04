# Frontend

> **Status: planned — not yet implemented.**

The frontend will be a Next.js web application served within the local kind cluster and consuming the [Backend API](../backend/README.md).

## Planned Stack

- **Next.js 14+** (App Router)
- **TypeScript**
- **Tailwind CSS**

## Planned Local Development

```bash
# From this directory
npm install
npm run dev     # http://localhost:3000
```

## Backend Connection

The frontend will communicate with the backend via the Kubernetes service name `backend:8000` inside the cluster, and via `http://localhost:8000` in local dev (port-forwarded).

The base URL will be configured through an environment variable:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Deployment

Will follow the same Kustomize + Skaffold pattern as the backend. See [infra/k8s/README.md](../../infra/k8s/README.md).

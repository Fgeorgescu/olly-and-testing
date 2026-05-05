# Frontend

Next.js marketplace UI for the Integrador platform.

## Stack

| Library | Purpose |
|---------|---------|
| Next.js 15 (App Router) | React framework |
| TypeScript | Type safety |
| Tailwind CSS | Styling |
| TanStack Query | Server state, caching |
| Vitest + Testing Library | Unit tests |

## Local Development

```bash
# From the repo root — starts everything
make setup

# Or run the frontend alone (backend must be up)
cd apps/frontend && npm run dev   # http://localhost:3000
```

## Pages

| Route | Description |
|-------|-------------|
| `/` | Home — search and browse listings |
| `/items/[id]` | Item detail — hold, confirm, release |
| `/items/new` | Post a new listing |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend base URL |

## Backend Connection

The frontend talks to the backend via `NEXT_PUBLIC_API_URL`. All API calls are defined in [`src/lib/api.ts`](src/lib/api.ts).

Authentication is not yet implemented. The backend injects a fixed anonymous seller ID server-side for all item creation requests.

## Testing

```bash
cd apps/frontend
npm test          # run Vitest unit tests
npm run build     # type-check + production build
```

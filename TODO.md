# TODO

Next steps worth doing, roughly in priority order. Move items to specs or GitHub issues before starting implementation.

## Backend

- [ ] **Auth / user model** — replace `seller_id`/`buyer_id` request fields with a real identity layer (JWT or session); unblocks hiding seller contact until hold is placed
- [ ] **Hold expiry** — auto-release holds after a configurable TTL (e.g. 48 h) so stale holds don't block listings indefinitely
- [ ] **Full-text search backend** — implement `FullTextSearchBackend` using PostgreSQL `tsvector`/`tsquery`; swap via `SEARCH_BACKEND=fulltext`
- [ ] **Price field** — add optional price to item listings (currently contact-based only)
- [ ] **Image uploads** — attach photos to listings; likely needs object storage (S3-compatible)
- [ ] **Pagination cursor** — replace page/offset with a cursor for stable pagination under concurrent inserts

## Frontend

- [ ] **Scaffold Next.js app** — bootstrap `apps/frontend/` (Next.js 14+, TypeScript, Tailwind)
- [ ] **Home page + search** — implement `home-search.md` spec
- [ ] **Post item form** — implement `post-item.md` spec
- [ ] **Item detail + purchase flow** — implement `item-detail.md` spec (hold, confirm, release)

## Infrastructure

- [ ] **PostgreSQL StatefulSet** — add Postgres to `infra/k8s/base/` so `make dev` spins up the full stack
- [ ] **Alembic init container** — run `alembic upgrade head` as a k8s init container before the backend pod starts
- [ ] **Secrets management** — move `DATABASE_URL` and other secrets out of overlays into a proper secret store (Sealed Secrets or external-secrets)

## Observability

- [ ] **Grafana dashboard** — add panels for `item_search_total`, `item_hold_total`, `item_sold_total`, and hold-to-sold conversion rate
- [ ] **Alerting rules** — add PrometheusRule for high error rate on `/api/v1/items`

## Testing

- [ ] **k6 smoke test** — add a smoke script that hits `/api/v1/items` and `POST /api/v1/items` under light load
- [ ] **LitmusChaos experiment** — `pod-delete` on the backend; verify items API recovers within the steady-state SLO
- [ ] **Contract tests** — add Schemathesis or similar to verify the OpenAPI spec matches the actual API behaviour

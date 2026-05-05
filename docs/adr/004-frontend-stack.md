# ADR-004: Frontend Stack

**Date:** 2026-05-04
**Status:** Accepted

## Context

The project needs a user-facing frontend for three features: browsing/searching items, viewing item detail and initiating a hold, and posting a new item. The backend is a FastAPI service; the primary focus of the project is infrastructure and observability, so the frontend stack should be productive but not over-engineered.

Key requirements driving the decision:

- Search state (query, category, tags, page) must live in the URL so links are shareable and the browser back button works.
- The purchase/hold flow involves status transitions (`available → on_hold → sold`) that multiple components need to react to; manual state synchronisation across components would be error-prone.
- The team wants the same three-tier testing approach used in the backend (fast unit → integration → e2e).

## Decision

| Concern | Choice | Rejected alternatives |
|---|---|---|
| Framework | **Next.js 14+ App Router** (TypeScript) | Vite + React SPA — loses SSR/file-based routing; Create React App — deprecated |
| Styling | **Tailwind CSS** | CSS Modules, styled-components |
| Data fetching / cache | **TanStack Query v5** | bare `fetch` + `useEffect` — no cache, manual re-sync after mutations |
| URL search state | **nuqs** | `useSearchParams` from Next.js — boilerplate; react-router's `useSearchParams` — not applicable |
| Unit tests | **Vitest + React Testing Library** | Jest — slower in Vite/Next.js ecosystem |
| API mocking (integration) | **MSW v2** | manual fetch stubs — brittle |
| Browser e2e | **Playwright** | Cypress — heavier install, slower parallelism |

### Why TanStack Query over bare fetch

TanStack Query's `queryKey` is the cache identity. Changing any filter param causes an automatic re-fetch with no manual `useEffect` dependency array maintenance. After mutations (place hold, release hold, confirm), calling `queryClient.invalidateQueries({ queryKey: ['items', itemId] })` refreshes the item detail everywhere it is rendered. This is essential for the `available → on_hold → sold` state machine, where stale UI would show an incorrect purchase button.

### Why nuqs

URL state must survive page reload and be shareable. nuqs provides typed, schema-validated bindings between URL search params and React state, integrating cleanly with the Next.js App Router. This is simpler than writing the serialisation/deserialisation manually.

## Consequences

- `apps/frontend/` is a standalone Next.js project. It calls the backend via `NEXT_PUBLIC_API_URL` (env var), which is `http://localhost:8000` locally and the backend service URL in k8s.
- All server-state lives in TanStack Query; `useState` is used only for purely local UI state (modal open/closed, form field values before submission).
- Three `package.json` test scripts: `test:unit` (Vitest), `test:integration` (Vitest + MSW), `test:e2e` (Playwright).
- CI adds a `frontend-unit` job; integration and e2e frontend jobs are added when the test suite is non-trivial.

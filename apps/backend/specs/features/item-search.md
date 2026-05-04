# Item Search

**Status**: Approved
**Author**: <!-- GitHub handle -->
**Created**: 2026-05-04
**Last updated**: 2026-05-04

---

## 1. Overview

Buyers can browse and search all listings from the home page. The search endpoint supports free-text queries and filters by category and tags. Results are paginated to avoid saturating backend services. Items with status `on_hold` are included in results but flagged so the frontend can indicate they are not purchasable.

The search logic must be isolated behind a well-defined interface so the underlying algorithm can be swapped at any time — from a simple SQL `ILIKE` to PostgreSQL full-text search or an external engine — without changing the API contract or any calling code.

---

## 2. Product Requirements

### User Stories

- As a **buyer**, I want to **browse all available items** so that **I can discover what is for sale**.
- As a **buyer**, I want to **search by keyword** so that **I can find specific items quickly**.
- As a **buyer**, I want to **filter by category or tag** so that **I can narrow results to what I need**.
- As a **buyer**, I want to **see on-hold items in results** so that **I know they exist even if I cannot purchase them now**.
- As a **buyer**, I want **paginated results** so that **the page loads quickly and I am not overwhelmed**.

### Acceptance Criteria

- [ ] Calling the endpoint with no filters returns all non-sold listings, newest first
- [ ] A keyword query matches title and description (case-insensitive, partial match)
- [ ] Results can be filtered by one or more categories
- [ ] Results can be filtered by one or more tags
- [ ] Items with status `on_hold` appear in results; `sold` items do not appear
- [ ] Results are paginated; default page size is 20, max is 100
- [ ] The response includes `total` so the frontend can render pagination controls
- [ ] Each result includes `status` so the frontend can visually distinguish on-hold items
- [ ] Swapping the search backend requires no changes to the route or response schema

### Business Rules

- `sold` items are excluded from all results
- `on_hold` items are included with `status: "on_hold"`
- Default sort is `created_at` descending (newest first); relevance sorting is out of scope
- An empty result set returns `200` with `items: []`, not `404`

---

## 3. Technical Requirements

### API Endpoints

| Method | Path | Description | Auth required? |
|--------|------|-------------|----------------|
| `GET` | `/api/v1/items` | List / search listings with pagination | No |

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `q` | `string` | — | Free-text search on title and description |
| `category` | `string[]` | — | Filter by category (repeatable: `?category=electronics&category=books`) |
| `tags` | `string[]` | — | Filter by tag (repeatable) |
| `page` | `int` | `1` | Page number (1-indexed) |
| `limit` | `int` | `20` | Items per page (max 100) |

### Search Abstraction

All search logic must be implemented behind a `SearchBackend` protocol. The route handler only depends on this interface; the concrete implementation is injected via FastAPI's dependency injection.

```python
from typing import Protocol

class SearchBackend(Protocol):
    async def search(self, query: SearchQuery) -> SearchResult:
        ...
```

**Planned backends** — each lives in `app/search/backends/<name>.py`; swap by changing `SEARCH_BACKEND` env var:

| Backend | `SEARCH_BACKEND` value | Algorithm |
|---------|------------------------|-----------|
| `SimpleSearchBackend` | `simple` | SQL `ILIKE` on title + description |
| `FullTextSearchBackend` | `fulltext` | PostgreSQL `tsvector` / `tsquery` |
| `ExternalSearchBackend` | `external` | Elasticsearch / OpenSearch |

The active backend is selected at startup in `app/search/factory.py` and registered as a FastAPI dependency.

### Data Models

```python
class SearchQuery(BaseModel):
    q: str | None
    categories: list[ItemCategory]
    tags: list[ItemTag]
    page: int           # >= 1
    limit: int          # 1–100

class ItemSummary(BaseModel):
    id: UUID
    title: str
    category: ItemCategory
    status: ItemStatus
    tags: list[ItemTag]
    seller_id: UUID
    created_at: datetime

class ItemListResponse(BaseModel):
    items: list[ItemSummary]
    total: int          # total matching records across all pages
    page: int
    limit: int
```

### Integrations

- **Item listing feature**: reads from the same items store
- **Config module**: `SEARCH_BACKEND` env var selects the active backend at startup

### Non-Functional Requirements

- **Flexibility**: zero search logic in the route layer; all algorithm details are inside the active `SearchBackend` implementation.
- **Performance**: < 200 ms p99 for up to 10 k listings on `SimpleSearchBackend`; add DB indexes on `status`, `category`, `created_at`.
- **Pagination safety**: `limit` is capped at 100 server-side regardless of the client request; prevents accidental full-table scans.
- **Observability**: emit `item_search_total` counter labeled with `backend` (active backend name), `has_query` (bool), `has_filters` (bool). Enables Grafana comparison between backends.
- **Error handling**:
  - `422` if `page < 1`, `limit < 1`, or `limit > 100`

---

## 4. Out of Scope

- Relevance ranking / scoring (initial backend returns newest-first regardless of query)
- Geo-based or distance filtering
- Saved searches / search history
- Sorting options other than newest-first
- Runtime backend hot-swap (startup only)

---

## 5. Open Questions

| # | Question | Owner | Resolution |
|---|----------|-------|------------|
| 1 | Should the home page use a separate "featured" endpoint or this same one with no filters? | | Same endpoint, no filters, for simplicity |
| 2 | Should `limit` have a minimum below 20 for mobile clients needing smaller pages? | | Allow `limit=1` as minimum; leave it to the client |
| 3 | Should the backend ever auto-switch backends based on load? | | Out of scope; operator switches via config deploy |

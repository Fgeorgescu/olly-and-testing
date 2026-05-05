# Home Page & Search

**Status**: Approved
**Author**: <!-- GitHub handle -->
**Created**: 2026-05-04
**Last updated**: 2026-05-04
**Backend spec**: [`apps/backend/specs/features/item-search.md`](../../../backend/specs/features/item-search.md)

---

## 1. Overview

The home page is the buyer's entry point. It shows a grid of recent listings and a search bar. Buyers can type a keyword and optionally filter by category or tag to narrow results. On-hold items are visible in the grid but have a visual indicator showing they are not available. Results are paginated to keep page loads fast.

---

## 2. User-Facing Requirements

### User Stories

- As a **buyer**, I want to **see recent listings on arrival** so that **I can discover items without searching**.
- As a **buyer**, I want to **search by keyword** so that **I can find what I am looking for**.
- As a **buyer**, I want to **filter by category or tag** so that **I can narrow results**.
- As a **buyer**, I want to **see at a glance which items are on hold** so that **I know not to expect them immediately**.
- As a **buyer**, I want **pagination controls** so that **I can browse all results without the page being slow**.

### Acceptance Criteria

- [ ] On load the page fetches and displays the first page of listings (newest first, no filters)
- [ ] Typing in the search bar debounces and triggers a new `GET /api/v1/items?q=...` request
- [ ] Selecting a category or tag filter re-fetches with the updated params; previous results are replaced
- [ ] On-hold items render with a visual "On hold" badge; their card is not clickable for purchase
- [ ] Sold items never appear
- [ ] Pagination controls allow moving to next/previous pages
- [ ] The current page, total results, and total pages are shown
- [ ] Clearing the search bar returns to the unfiltered list

### UI States

| State | Trigger | What the user sees |
|-------|---------|--------------------|
| Loading | Initial fetch or new search | Skeleton cards in the grid |
| Populated | Results returned | Item cards grid |
| Empty | `items: []` returned | "No items found" message |
| Error | API error | Error banner + retry button |
| On hold item | `status: "on_hold"` | Card with "On hold" badge, muted appearance |

---

## 3. Visual / UX Notes

### Page Layout

```
┌───────────────────────────────────────────┐
│ Nav                          [Post item]  │
├───────────────────────────────────────────┤
│  [🔍 Search items...              ]       │
│  Category: [All ▾]  Tags: [All ▾]        │
├───────────────────────────────────────────┤
│  ┌────────┐ ┌────────┐ ┌────────┐        │
│  │ Item   │ │ Item   │ │ Item   │        │
│  │        │ │ON HOLD │ │        │        │
│  └────────┘ └────────┘ └────────┘        │
│  ┌────────┐ ┌────────┐ ...               │
│  │ Item   │ │ Item   │                   │
│  └────────┘ └────────┘                   │
├───────────────────────────────────────────┤
│  ← Prev   Page 1 of 5 (92 results)  Next →│
└───────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility |
|-----------|---------------|
| `SearchBar` | Controlled input; debounces 300 ms before triggering search |
| `CategoryFilter` | Single-select dropdown from predefined categories + "All" option |
| `TagFilter` | Multi-select from predefined tags |
| `ItemGrid` | Renders the list of `ItemCard` components |
| `ItemCard` | Displays item summary; shows "On hold" badge when `status === "on_hold"`; links to `/items/{id}` |
| `Pagination` | Next / prev controls; displays current page and total |
| `SkeletonCard` | Placeholder shown while loading |

### Interaction Notes

- **Search debounce**: 300 ms after the user stops typing; avoids a request per keystroke
- **Filter changes**: immediate re-fetch (no debounce needed for dropdown)
- **On-hold cards**: navigating to the item detail page is still allowed (buyer can see details); only the purchase action is blocked there
- **Pagination**: changing page scrolls the user to the top of the grid
- **URL state**: `q`, `category`, `tags`, and `page` should be reflected in the URL query string so results are shareable and the back button works

---

## 4. Integration Points

### API Calls

| Trigger | Method | Endpoint | Notes |
|---------|--------|----------|-------|
| Page load / filter change | `GET` | `/api/v1/items` | Params: `q`, `category[]`, `tags[]`, `page`, `limit=20` |

### State / Data Flow

Search params are derived from the URL query string (single source of truth). Components read from and write to the URL; the router triggers a re-fetch on change. No global state store required for the initial implementation.

### Error Handling

| Scenario | HTTP status | User-facing message |
|----------|-------------|---------------------|
| Server error | `5xx` | "Could not load items. Try again." + retry button |
| Invalid params | `422` | Should not happen if the UI only sends valid values; log and show generic error |

---

## 5. Observability

### User Interactions to Track

| Interaction | Suggested event name | Notes |
|-------------|---------------------|-------|
| Search query submitted | `search_query_submitted` | Include `has_query`, `has_category_filter`, `has_tag_filter` |
| Category filter applied | `search_category_filter_applied` | Include `category` value |
| Tag filter applied | `search_tag_filter_applied` | Include `tags` values |
| Pagination — next/prev | `search_page_changed` | Include `direction: next\|prev` and `page` number |
| Item card clicked | `search_item_clicked` | Include `item_id` and `item_status` |

### Error Monitoring

- API errors (5xx) on the search fetch should be forwarded to the error tracker with the query params used.

---

## 6. Out of Scope

- Relevance-ranked results (initial sort is newest first)
- Infinite scroll (pagination controls only for now)
- Saved searches or search history
- Geo-based filtering

---

## 7. Open Questions

| # | Question | Owner | Resolution |
|---|----------|-------|------------|
| 1 | Should the initial page show a curated set (e.g. featured items) or purely newest? | | Newest first for now |
| 2 | Should filters be collapsed on mobile? | | Defer to implementation; not a spec concern |

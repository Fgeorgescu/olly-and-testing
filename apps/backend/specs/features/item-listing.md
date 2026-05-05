# Item Listing

**Status**: Approved
**Author**: <!-- GitHub handle -->
**Created**: 2026-05-04
**Last updated**: 2026-05-04

---

## 1. Overview

Sellers can create, update, and delete item listings. Each listing describes a second-hand or new item available for sale. Listings are the core entity of the platform — all other features (search, purchase) depend on them existing.

---

## 2. Product Requirements

### User Stories

- As a **seller**, I want to **post an item for sale** so that **potential buyers can find and contact me**.
- As a **seller**, I want to **edit my listing** so that **I can correct mistakes or update availability**.
- As a **seller**, I want to **delete my listing** so that **I can remove items that are no longer available**.

### Acceptance Criteria

- [ ] A seller can submit a listing with title, description, category, and optional tags
- [ ] The listing is created with status `available`
- [ ] A seller can update only their own listings
- [ ] A seller can delete only their own listings
- [ ] Deleting a listing that is `on_hold` is not allowed until the hold is released
- [ ] All required fields are validated; missing or invalid input returns a 422

### Business Rules

- **Predefined categories**: `electronics`, `clothing`, `furniture`, `vehicles`, `sports`, `books`, `other`
- **Predefined tags** (select from list, no custom values): `new`, `used`, `refurbished`, `negotiable`, `urgent`, `bundle`
- **Status transitions**: A listing always starts as `available`. Status changes to `on_hold` or `sold` are managed by the purchase-hold flow, not this feature.
- A seller cannot list the same item twice (deduplication is out of scope for now).

---

## 3. Technical Requirements

### API Endpoints

| Method | Path | Description | Auth required? |
|--------|------|-------------|----------------|
| `POST` | `/api/v1/items` | Create a new listing | Yes (seller) |
| `GET` | `/api/v1/items/{id}` | Get a single listing by ID | No |
| `PUT` | `/api/v1/items/{id}` | Update a listing | Yes (owner only) |
| `DELETE` | `/api/v1/items/{id}` | Delete a listing | Yes (owner only) |

### Data Models

```python
from enum import Enum
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class ItemCategory(str, Enum):
    electronics = "electronics"
    clothing = "clothing"
    furniture = "furniture"
    vehicles = "vehicles"
    sports = "sports"
    books = "books"
    other = "other"

class ItemTag(str, Enum):
    new = "new"
    used = "used"
    refurbished = "refurbished"
    negotiable = "negotiable"
    urgent = "urgent"
    bundle = "bundle"

class ItemStatus(str, Enum):
    available = "available"
    on_hold = "on_hold"
    sold = "sold"

class ItemCreate(BaseModel):
    title: str          # max 120 chars
    description: str    # max 2000 chars
    category: ItemCategory
    tags: list[ItemTag] = []

class ItemUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    category: ItemCategory | None = None
    tags: list[ItemTag] | None = None

class ItemResponse(BaseModel):
    id: UUID
    title: str
    description: str
    category: ItemCategory
    status: ItemStatus
    tags: list[ItemTag]
    seller_id: UUID
    created_at: datetime
    updated_at: datetime
```

### Integrations

- **Auth module** (future): `seller_id` is taken from the authenticated user's identity — it is never part of the request body. Until auth is implemented, a fixed placeholder UUID (`00000000-0000-0000-0000-000000000001`) is injected server-side via a stub `get_current_user` dependency in `app/api/v1/items.py`.
- **Purchase-hold feature**: controls status transitions; this feature must not change status directly.

### Non-Functional Requirements

- **Performance**: `GET /api/v1/items/{id}` must respond in < 100 ms p99.
- **Security**: `PUT` and `DELETE` must verify the caller owns the listing; return 403 otherwise.
- **Error handling**:
  - `404` if listing not found
  - `403` if caller is not the owner
  - `409` if attempting to delete an `on_hold` listing
  - `422` for validation errors

---

## 4. Observability

### Metrics

| Metric | Type | Labels | Emitted when |
|--------|------|--------|--------------|
| `item_events_total` | Counter | `event: created` | `POST /api/v1/items` succeeds |
| `item_events_total` | Counter | `event: deleted` | `DELETE /api/v1/items/{id}` succeeds |

### Dashboards

- **Item Lifecycle Events** — panels showing rate of items created and deleted over time.

### Alerts

- Alert if `rate(item_events_total{event="created"}[5m]) == 0` for an extended window during expected high-traffic hours (indicates a potential ingestion problem).

---

## 5. Out of Scope

- Image uploads
- Listing expiry / auto-archival
- Price field (contact-based negotiation; price may be added later)
- Custom or user-defined tags

---

## 6. Open Questions

| # | Question | Owner | Resolution |
|---|----------|-------|------------|
| 1 | Should tags be multi-select with a max count? | | |
| 2 | Do we need a `draft` status before `available`? | | |

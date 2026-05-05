# Purchase / Hold Flow

**Status**: Approved
**Author**: <!-- GitHub handle -->
**Created**: 2026-05-04
**Last updated**: 2026-05-04

---

## 1. Overview

When a buyer wants to purchase an item, they place it on hold. Holding reveals the seller's contact info so both parties can coordinate in person. After the transaction happens, **both the buyer and the seller must independently confirm** it was completed. The item is only marked `sold` once both confirmations are received. Either party can release the hold at any point before both have confirmed, returning the item to `available`.

---

## 2. Product Requirements

### User Stories

- As a **buyer**, I want to **place an item on hold** so that **it is reserved while I arrange the purchase**.
- As a **buyer**, I want to **see the seller's contact information after placing a hold** so that **I can reach out to meet and transact**.
- As a **buyer**, I want to **confirm the purchase was completed** so that **the item is marked as sold**.
- As a **seller**, I want to **confirm the purchase was completed** so that **the item is removed from the marketplace**.
- As a **buyer** or **seller**, I want to **release the hold** so that **the item becomes available again if the transaction does not happen**.

### Acceptance Criteria

- [ ] A buyer can place a hold on an `available` item; item status changes to `on_hold`
- [ ] After placing a hold, the buyer receives the seller's contact info in the response
- [ ] The buyer can call `POST /confirm`; the hold records `buyer_confirmed = true`
- [ ] The seller can call `POST /confirm`; the hold records `seller_confirmed = true`
- [ ] When **both** buyer and seller have confirmed, the item transitions to `sold` atomically
- [ ] Confirming only one side does not change the item status
- [ ] Either party can call `DELETE /hold` to release; item returns to `available` and confirmations are cleared
- [ ] Attempting to hold an already `on_hold` or `sold` item returns `409`
- [ ] A party that already confirmed cannot confirm again (returns `409`)

### Business Rules

- Only `available` items can be placed on hold
- Only one hold is active per item at any time
- Seller contact info is only visible to the active holder
- The `sold` transition is triggered automatically when the second `/confirm` is received — no separate "mark as sold" action exists
- Releasing the hold before both confirm cancels the transaction; confirmations already given are discarded
- A seller cannot hold their own listing (`buyer_id` must differ from `seller_id`)
- On-hold items appear in search results but cannot be held again

---

## 3. Technical Requirements

### API Endpoints

| Method | Path | Description | Auth required? |
|--------|------|-------------|----------------|
| `POST` | `/api/v1/items/{id}/hold` | Place a hold; returns seller contact | Yes (buyer) |
| `DELETE` | `/api/v1/items/{id}/hold` | Release the hold | Yes (buyer or seller) |
| `GET` | `/api/v1/items/{id}/contact` | Get seller contact (active holder only) | Yes |
| `POST` | `/api/v1/items/{id}/confirm` | Confirm the in-person transaction | Yes (buyer or seller) |

### State Machine

```
available
  └─[POST /hold]──────────────▶ on_hold
                                   │
                         ┌─────────┴──────────┐
                [DELETE /hold]          [POST /confirm × 2]
                (either party)          (buyer AND seller)
                         │                     │
                         ▼                     ▼
                     available               sold
```

Intermediate state (one confirm received, waiting for the other) remains `on_hold`. The transition to `sold` fires atomically when the second `/confirm` arrives.

### Data Models

```python
class HoldResponse(BaseModel):
    item_id: UUID
    held_by: UUID               # buyer user ID
    held_at: datetime
    buyer_confirmed: bool
    seller_confirmed: bool
    seller_contact: SellerContact

class SellerContact(BaseModel):
    seller_id: UUID
    display_name: str
    email: str

class ConfirmResponse(BaseModel):
    item_id: UUID
    confirmed_by: str           # "buyer" | "seller"
    buyer_confirmed: bool
    seller_confirmed: bool
    status: ItemStatus          # "on_hold" until both confirm, then "sold"

class HoldReleaseResponse(BaseModel):
    item_id: UUID
    status: ItemStatus          # "available"
```

### Integrations

- **Item listing feature**: reads and updates `items.status`; transitions must be atomic (single DB transaction).
- **Auth module** (future): caller identity resolves to buyer or seller role. Until auth exists, `buyer_id` is an explicit request field and `seller_id` is taken from the listing.

### Non-Functional Requirements

- **Atomicity**: the `sold` transition (status update + hold record finalization) must happen in a single DB transaction to prevent races.
- **Security**:
  - `GET /contact` returns `403` if caller is not the active holder
  - `POST /confirm` returns `403` if caller is neither the holder nor the seller
  - `DELETE /hold` returns `403` if caller is neither the holder nor the seller
- **Error handling**:
  - `404` — item not found
  - `409` — item already `on_hold` or `sold` (on `POST /hold`)
  - `409` — caller already confirmed (on `POST /confirm`)
  - `403` — unauthorized caller
- **Observability**: see Observability section below.

---

## 4. Observability

### Metrics

| Metric | Type | Labels | Emitted when |
|--------|------|--------|--------------|
| `item_events_total` | Counter | `event: on_hold` | `POST /api/v1/items/{id}/hold` succeeds |
| `item_events_total` | Counter | `event: hold_released`, `released_by: buyer\|seller` | `DELETE /api/v1/items/{id}/hold` succeeds |
| `item_events_total` | Counter | `event: confirmed`, `confirmed_by: buyer\|seller` | `POST /api/v1/items/{id}/confirm` records a confirmation |
| `item_events_total` | Counter | `event: sold` | Both parties confirm; item transitions to `sold` |

### Dashboards

- **Item Lifecycle Events** — panels for hold rate, release rate, and sold rate over time.

### Alerts

- Alert if `rate(item_events_total{event="sold"}[1h]) == 0` for an extended period during business hours (may indicate the confirmation flow is broken).

---

## 5. Out of Scope

- Automatic hold expiry (e.g., release after 48 h with no confirmation)
- In-platform messaging between buyer and seller
- Payment processing
- Dispute resolution if one party confirms and the other does not
- Hold history / audit log beyond the current active hold

---

## 6. Open Questions

| # | Question | Owner | Resolution |
|---|----------|-------|------------|
| 1 | Should the seller's email be shown directly, or via a contact form to avoid exposing PII? | | Direct email for now; revisit when auth is added |
| 2 | What happens if the seller confirms but the buyer never does? | | Hold stays open indefinitely; expiry is out of scope |
| 3 | Can a buyer place a hold on multiple items simultaneously? | | Yes, no restriction per buyer for now |

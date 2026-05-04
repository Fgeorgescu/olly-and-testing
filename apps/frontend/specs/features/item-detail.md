# Item Detail Page

**Status**: Approved
**Author**: <!-- GitHub handle -->
**Created**: 2026-05-04
**Last updated**: 2026-05-04
**Backend spec**: [`apps/backend/specs/features/purchase-hold.md`](../../../backend/specs/features/purchase-hold.md)

---

## 1. Overview

The item detail page shows the full listing to any visitor. For buyers, it provides a "Purchase" button that places the item on hold and reveals the seller's contact information in a popup so they can arrange the in-person transaction. After the meeting, both parties must confirm the purchase through the same page. Either party can release the hold at any time before both have confirmed.

---

## 2. User-Facing Requirements

### User Stories

- As a **buyer**, I want to **see all the details of an item** so that **I can decide whether to purchase it**.
- As a **buyer**, I want to **click a button to hold the item** so that **I reserve it while I contact the seller**.
- As a **buyer**, I want to **see the seller's contact info after placing a hold** so that **I know how to reach them**.
- As a **buyer**, I want to **confirm the purchase was completed** so that **the item is marked sold**.
- As a **seller**, I want to **confirm the purchase was completed** so that **my listing is closed**.
- As a **buyer** or **seller**, I want to **release the hold** so that **the item becomes available again if the deal falls through**.

### Acceptance Criteria

- [ ] The page displays title, description, category, tags, status, and post date
- [ ] If status is `available`, a "Purchase" button is shown
- [ ] Clicking "Purchase" calls `POST /api/v1/items/{id}/hold` and opens the seller contact popup
- [ ] The popup shows the seller's name and email
- [ ] While the item is `on_hold`, the page shows a hold status section (who holds it, when)
- [ ] The active holder (buyer) sees a "Confirm purchase" button and a "Release hold" button
- [ ] The seller sees a "Confirm purchase" button and a "Release hold" button on their own listing
- [ ] After one party confirms, their "Confirm purchase" button changes to a disabled "Confirmed" state
- [ ] When both have confirmed, the item status updates to `sold` and both buttons are replaced with a "Sale complete" message
- [ ] If the item is `sold`, no purchase or hold actions are shown
- [ ] If the item is `on_hold` and the viewer is neither the holder nor the seller, only a "Currently on hold" notice is shown (no action buttons)

### UI States

| State | Trigger | What the user sees |
|-------|---------|--------------------|
| Available (visitor) | `status: available` | Full details + "Purchase" button |
| Placing hold | "Purchase" clicked | Button spinner |
| On hold — contact popup | Hold placed successfully | Seller contact modal |
| On hold — active holder | Holder views page | Hold info + "Confirm" + "Release" buttons |
| On hold — seller | Seller views page | Hold info + "Confirm" + "Release" buttons |
| On hold — other visitor | Third party views page | "Currently on hold" notice; no actions |
| One side confirmed | Either party confirmed | That party's button shows "Confirmed ✓"; other still pending |
| Both confirmed (sold) | `status: sold` | "Sale complete" banner; no actions |
| Error | API error on any action | Inline error message near the button |

---

## 3. Visual / UX Notes

### Page Layout

```
┌────────────────────────────────────────────┐
│ Nav                                        │
├────────────────────────────────────────────┤
│ [Category badge]  [Status badge]           │
│ Title                                      │
│ Tags: [new] [negotiable]                   │
│                                            │
│ Description                                │
│ ...                                        │
│                                            │
│ Posted: 2026-05-01                         │
├────────────────────────────────────────────┤
│ ── Purchase section ──                     │
│ [Purchase button]   (available only)       │
│                                            │
│ — or —                                     │
│                                            │
│ On hold since 2026-05-03                   │
│ [Confirm purchase]  [Release hold]         │
│  (buyer/seller only)                       │
└────────────────────────────────────────────┘
```

### Seller Contact Popup

```
┌──────────────────────────────┐
│ Seller contact               │
│                              │
│ Name:  John Doe              │
│ Email: john@example.com      │
│                              │
│        [Close]               │
└──────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility |
|-----------|---------------|
| `ItemDetail` | Page root; fetches item and renders all sections |
| `ItemMeta` | Displays title, description, category, tags, dates |
| `StatusBadge` | Colour-coded badge for `available` / `on_hold` / `sold` |
| `PurchaseSection` | Renders the correct action area based on item status and viewer role |
| `SellerContactModal` | Popup showing seller's name and email |
| `HoldActions` | "Confirm purchase" and "Release hold" buttons with their loading/disabled states |

### Interaction Notes

- **Contact popup**: stays open until the buyer dismisses it. Buyer can reopen it via `GET /api/v1/items/{id}/contact` (a "View seller contact" link while on hold).
- **Confirm button**: after clicking, shows a spinner then switches to a disabled "Confirmed ✓" state. Cannot be clicked again.
- **"Sale complete" banner**: replaces both action buttons when `status` transitions to `sold`; auto-visible on next page load or via polling/refresh (no WebSocket required at this stage).
- **Viewer role resolution**: determined client-side from the user's identity vs. `seller_id` and hold `held_by`. Until auth is implemented, role is passed as a query param for development purposes only.

---

## 4. Integration Points

### API Calls

| Trigger | Method | Endpoint | Notes |
|---------|--------|----------|-------|
| Page load | `GET` | `/api/v1/items/{id}` | Full item detail |
| "Purchase" click | `POST` | `/api/v1/items/{id}/hold` | Returns `seller_contact` |
| "View contact" click | `GET` | `/api/v1/items/{id}/contact` | Active holder only |
| "Confirm purchase" click | `POST` | `/api/v1/items/{id}/confirm` | Buyer or seller |
| "Release hold" click | `DELETE` | `/api/v1/items/{id}/hold` | Buyer or seller |

### State / Data Flow

Item data is fetched on mount and stored locally in the page component. After any mutation (hold, confirm, release) the item is re-fetched to get the updated `status` and hold state — no optimistic updates in the initial implementation.

### Error Handling

| Scenario | HTTP status | User-facing message |
|----------|-------------|---------------------|
| Item not found | `404` | "This item no longer exists." |
| Item already on hold | `409` (on hold) | "This item was just taken. Check back later." |
| Already confirmed | `409` (confirm) | "You have already confirmed this purchase." |
| Unauthorized action | `403` | "You are not allowed to do this." |
| Server error | `5xx` | "Something went wrong. Please try again." |

---

## 5. Out of Scope

- Real-time status updates (WebSocket / SSE); user refreshes to see latest state
- In-platform messaging
- Dispute resolution UI
- Image gallery

---

## 6. Open Questions

| # | Question | Owner | Resolution |
|---|----------|-------|------------|
| 1 | Should the seller contact popup be shown again on page reload while on hold, or only at the moment of hold placement? | | Accessible at any time via the "View contact" link while on hold |
| 2 | How does the page know the viewer's role before auth is implemented? | | Dev-only query param `?viewer_id=`; removed once auth is added |

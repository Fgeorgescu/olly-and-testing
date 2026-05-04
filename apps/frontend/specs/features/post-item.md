# Post an Item for Sale

**Status**: Approved
**Author**: <!-- GitHub handle -->
**Created**: 2026-05-04
**Last updated**: 2026-05-04
**Backend spec**: [`apps/backend/specs/features/item-listing.md`](../../../backend/specs/features/item-listing.md)

---

## 1. Overview

Sellers fill out a form to create a new listing. The form collects the item's title, description, category, and optional tags. On successful submission the seller is redirected to the item's detail page so they can verify how it looks to buyers.

---

## 2. User-Facing Requirements

### User Stories

- As a **seller**, I want to **fill out a form and post my item** so that **buyers can find it**.
- As a **seller**, I want to **see validation errors inline** so that **I can correct mistakes without losing my input**.
- As a **seller**, I want to **be taken to my listing after posting** so that **I can confirm it looks right**.

### Acceptance Criteria

- [ ] The form has fields for title, description, category (dropdown), and tags (multi-select)
- [ ] All required fields are validated client-side before submission
- [ ] Validation errors appear inline next to the relevant field
- [ ] On success the user is redirected to the item detail page (`/items/{id}`)
- [ ] On API error (422 / 5xx) an error banner is shown and the form remains filled

### UI States

| State | Trigger | What the user sees |
|-------|---------|--------------------|
| Idle | Page load | Empty form, submit button enabled |
| Validating | Submit clicked | Inline field errors if invalid |
| Submitting | Valid form submitted | Submit button disabled + spinner |
| Success | `201` from API | Redirect to `/items/{id}` |
| API Error | Non-201 response | Error banner above form; form stays filled |

---

## 3. Visual / UX Notes

### Page Layout

```
┌─────────────────────────────────┐
│ Nav                             │
├─────────────────────────────────┤
│ [Page title: "Post an item"]    │
│                                 │
│ Title          [____________]   │
│ Description    [____________]   │
│                [____________]   │
│ Category       [dropdown    ▾]  │
│ Tags           [multi-select]   │
│                                 │
│              [Post item button] │
└─────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility |
|-----------|---------------|
| `PostItemForm` | Owns form state, validation, and submission |
| `CategorySelect` | Renders the predefined category dropdown |
| `TagSelect` | Renders the predefined tags as a multi-select (checkboxes or pills) |
| `FieldError` | Displays inline validation messages |
| `ErrorBanner` | Displays API-level errors at the top of the form |

### Interaction Notes

- **Category** is a required single-select from the predefined list (`electronics`, `clothing`, `furniture`, `vehicles`, `sports`, `books`, `other`)
- **Tags** are optional; predefined list only (`new`, `used`, `refurbished`, `negotiable`, `urgent`, `bundle`); no free-text entry
- **Description** is a textarea; max 2 000 characters with a live counter
- **Title** max 120 characters
- Submit button is disabled while the request is in flight

---

## 4. Integration Points

### API Calls

| Trigger | Method | Endpoint | Notes |
|---------|--------|----------|-------|
| Form submit | `POST` | `/api/v1/items` | Body: `{ title, description, category, tags }` |

### State / Data Flow

Form state is local to `PostItemForm`. No global state is needed. On `201` the response body contains the new item's `id`; use it to build the redirect URL.

### Error Handling

| Scenario | HTTP status | User-facing message |
|----------|-------------|---------------------|
| Validation failed | `422` | Show field-level errors from `detail` array |
| Server error | `5xx` | "Something went wrong. Please try again." |

---

## 5. Out of Scope

- Image uploads
- Draft saving / auto-save
- Price field

---

## 6. Open Questions

| # | Question | Owner | Resolution |
|---|----------|-------|------------|
| 1 | Should the post form require authentication? | | Yes, once auth is added; for now any user can post |

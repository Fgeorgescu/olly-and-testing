# [Feature Name]

**Status**: Draft | Review | Approved | Implemented | Deprecated
**Author**: <!-- GitHub handle -->
**Created**: <!-- YYYY-MM-DD -->
**Last updated**: <!-- YYYY-MM-DD -->
**Backend spec**: <!-- link to corresponding backend spec if applicable -->

---

## 1. Overview

One paragraph describing what this page or feature does and what problem it solves for the user. Keep it user-facing — describe the experience, not the implementation.

---

## 2. User-Facing Requirements

### User Stories

- As a **[role]**, I want **[goal]** so that **[reason]**.

### Acceptance Criteria

- [ ] Criterion 1 — the observable, testable outcome
- [ ] Criterion 2

### UI States

List every state the UI can be in for this feature:

| State | Trigger | What the user sees |
|-------|---------|--------------------|
| Loading | Data fetch in flight | Skeleton / spinner |
| Empty | No results returned | Empty state message |
| Error | API error | Error message + retry |
| Populated | Data loaded | Normal view |
| (add more as needed) | | |

---

## 3. Visual / UX Notes

### Page Layout

Describe the page structure at a high level (header, main content area, sidebar, etc.). Wireframe sketches can be embedded as images or ASCII diagrams.

```
┌─────────────────────────────┐
│ Header / Nav                │
├─────────────────────────────┤
│ Main content                │
│                             │
└─────────────────────────────┘
```

### Component Responsibilities

List the key components on this page and what each one owns:

| Component | Responsibility |
|-----------|---------------|
| `ComponentName` | What it renders and what actions it handles |

### Interaction Notes

Describe key user interactions: what happens on click, hover, submit, etc. Focus on non-obvious behavior.

---

## 4. Integration Points

### API Calls

| Trigger | Method | Endpoint | Notes |
|---------|--------|----------|-------|
| Page load | `GET` | `/api/v1/...` | |
| Form submit | `POST` | `/api/v1/...` | |

### State / Data Flow

Describe how data flows through the page: what is fetched, what is stored locally, what is passed as props.

### Error Handling

| Scenario | HTTP status | User-facing message |
|----------|-------------|---------------------|
| Item not found | `404` | "This item no longer exists." |
| Unauthorized | `403` | "You don't have permission to do this." |

---

## 5. Out of Scope

- Item 1
- Item 2

---

## 6. Open Questions

| # | Question | Owner | Resolution |
|---|----------|-------|------------|
| 1 | | | |

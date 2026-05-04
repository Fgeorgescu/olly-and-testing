# [Feature Name]

**Status**: Draft | Review | Approved | Implemented | Deprecated
**Author**: <!-- GitHub handle -->
**Created**: <!-- YYYY-MM-DD -->
**Last updated**: <!-- YYYY-MM-DD -->

---

## 1. Overview

One paragraph describing what this feature does and what problem it solves for the user. Keep it business-facing — avoid implementation details here.

---

## 2. Product Requirements

### User Stories

- As a **[role]**, I want **[goal]** so that **[reason]**.
- As a **[role]**, I want **[goal]** so that **[reason]**.

### Acceptance Criteria

- [ ] Criterion 1 — the observable outcome that confirms this story is done
- [ ] Criterion 2
- [ ] Criterion 3

### Business Rules

- **Rule 1**: Constraint or invariant that must always hold (e.g., "a product price must be > 0").
- **Rule 2**: Edge case behavior (e.g., "out-of-stock items can still be browsed but not added to cart").

---

## 3. Technical Requirements

### API Endpoints

| Method | Path | Description | Auth required? |
|--------|------|-------------|----------------|
| `GET` | `/api/v1/...` | | No |
| `POST` | `/api/v1/...` | | Yes |

### Data Models

```python
# Pydantic request/response schemas or entity field list
class ExampleRequest(BaseModel):
    field: type
```

### Integrations

- List external services, databases, or other internal modules this feature depends on.

### Non-Functional Requirements

- **Performance**: Expected response time or throughput (e.g., "< 200 ms p99 under nominal load").
- **Security**: Auth requirements, input validation rules, sensitive data handling.
- **Error handling**: Which HTTP status codes are returned and when.
- **Observability**: Metrics or log events this feature should emit.

---

## 4. Out of Scope

List anything explicitly excluded from this spec to avoid scope creep.

- Item 1
- Item 2

---

## 5. Open Questions

| # | Question | Owner | Resolution |
|---|----------|-------|------------|
| 1 | | | |

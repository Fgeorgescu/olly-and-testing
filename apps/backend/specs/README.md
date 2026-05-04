# Specs

This directory is the source of truth for all backend features. Every feature starts as a spec before any code is written.

## Workflow

1. **Copy the template**: `cp _template.md features/<feature-name>.md`
2. **Fill it out**: complete the Overview, Product Requirements, and Technical Requirements sections
3. **Review**: open a PR; at least one reviewer must approve
4. **Implement**: once the spec is in `Approved` status, implementation can begin
5. **Update status**: mark the spec `Implemented` when the feature ships; `Deprecated` if it is removed

No implementation PR should be opened without a corresponding spec in `Approved` status.

## Lifecycle

```
Draft → Review → Approved → Implemented → Deprecated
```

| Status | Meaning |
|--------|---------|
| `Draft` | Work in progress, not ready for review |
| `Review` | Ready for team review |
| `Approved` | Reviewed and cleared for implementation |
| `Implemented` | Feature is live |
| `Deprecated` | Feature removed or replaced |

## File Naming

```
specs/features/<feature-name>.md
```

Use lowercase kebab-case: `product-catalog.md`, `checkout-flow.md`.

## Template

See [`_template.md`](_template.md) for the full spec structure.

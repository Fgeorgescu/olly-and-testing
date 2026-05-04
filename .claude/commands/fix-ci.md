Troubleshoot and fix a failing GitHub Actions CI run for this repository.

## Instructions

$ARGUMENTS may contain a specific run ID. If not provided, use the most recent failing run.

### 1. Identify the failing run

```bash
gh run list --repo Fgeorgescu/integrador --status failure --limit 5
```

If $ARGUMENTS is a run ID, skip listing and go directly to step 2 with that ID.
Otherwise pick the most recent failure.

### 2. Fetch the failure logs

```bash
gh run view <run-id> --repo Fgeorgescu/integrador --log-failed
```

### 3. Analyze

Read the full error output carefully. Identify:
- Which job and step failed
- The exact error message and its root cause
- Which source file(s) need to change

Do not guess. Read the relevant source files before making any change.

### 4. Fix

Apply the minimal change that resolves the root cause. Do not refactor surrounding code or fix unrelated issues.

### 5. Verify locally when possible

If the failing step is `pytest`, run the tests locally against the fix.
If the failing step is `ruff`, run `ruff check .` locally.

### 6. Commit and push

Write a commit message that names what was broken and why the fix resolves it.
Push and confirm GitHub triggers a new CI run.

### 7. Report

Summarize: what failed, what the root cause was, what was changed, and whether CI is now passing or pending.

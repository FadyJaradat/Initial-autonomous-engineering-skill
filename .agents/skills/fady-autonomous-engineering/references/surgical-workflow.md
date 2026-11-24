# Surgical implementation workflow

1. Establish current behavior and desired behavior. Reproduce bug where feasible. Identify root cause rather than patching symptoms blindly.
2. Inspect `git status`, closest symbols, callers and tests. Preserve pre-existing changes. Avoid files outside relevant scope.
3. Propose smallest correct patch; note compatibility, security and migration consequences. For important tradeoffs, challenge assumptions and write a brief decision record.
4. Edit only target functions/configurations. Avoid unrelated renames, formatting, new libraries or architecture churn. No automatic force-push, reset, rebases over others' work, or database destructive migrations.
5. Inspect `git diff --check`, scoped `git diff`, and run focused tests. Expand testing only for identified risk. Do not claim missing tests passed.
6. Record what changed, verification evidence and outstanding gaps in `HANDOFF.md`. Update map/runbook only if interfaces, files or commands actually changed.

When a small patch cannot safely satisfy requirements, explain why the broader patch is technically necessary. Do not optimize for line count at the expense of security and correctness.

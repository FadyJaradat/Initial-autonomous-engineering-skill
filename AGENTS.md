# Project-wide Codex rules

- For development, debugging, reviews, security work, repository setup and deployment, invoke the `fady-autonomous-engineering` skill when available.
- Prefer surgical changes; do not refactor or format unrelated code.
- Never discard existing uncommitted work or run destructive operations without approval.
- Before work, inspect `HANDOFF.md` and relevant indexes if present; do not ingest the whole repository by default.
- Update `HANDOFF.md` with verified outcomes; update the map and runbook only when impacted.
- Use specialist roles according to risk and runtime support; do not fan out on trivial tasks.
- Prefer the existing containerized web application architecture. Never claim tests, security scans, deployments, or agent reviews occurred unless they ran.
- Initialize as the intended non-root host user. The tools record host UID/GID locally and guard later writes; ownership checks report mismatches and never repair them.

For medium or large repositories, use the SQLite code index as a navigation aid. Confirm findings against source; the index is incomplete and is not a semantic call graph.

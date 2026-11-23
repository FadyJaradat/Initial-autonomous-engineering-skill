# Project-wide Codex rules
- For development, debugging, reviews, security work, repository setup and deployment, invoke the `fady-autonomous-engineering` skill when available.
- Prefer surgical changes; do not refactor or format unrelated code.
- Never discard existing uncommitted work or run destructive operations without approval.
- Before work, inspect `HANDOFF.md` and relevant indexes if present; do not ingest the whole repository by default.
- For task completion, update `HANDOFF.md` with actual outcomes; update mapping and runbook only if impacted.
- When supported, use specialist agents according to risk rather than activating them all by default.
- Containerized web application is the deployment preference. Preserve existing working infrastructure.
- Project-created files on supported Unix filesystems must be owned by `fady:fady`; check actual UID/GID first, and do not perform unsafe recursive ownership corrections.
- Never claim tests, security scans, deployment, or agent review occurred unless actually executed.

# Requirements for the reusable Codex skill

This document restates the published implementation requirements. Build and maintain `.agents/skills/fady-autonomous-engineering/` as a portable, installable Codex skill with a concise `SKILL.md`, on-demand references, templates, stdlib-only utilities, tests, and CI. Preserve existing work and never publish without explicit authorization.

## Behavior

- Orchestrate initialization, continuation, debugging, implementation, review, tests, security work and deployment planning. The skill is not a promise of agents, scheduled work, infinite memory, credentials or production access.
- Preserve seven logical roles: orchestrator, planner, backend developer, frontend developer, QA, source security reviewer and authorized web penetration-testing specialist. Use only relevant roles and only delegate when the runtime supports it. Avoid concurrent edits to the same file.
- Make surgical changes: diagnose root cause, inspect scoped dependencies, patch minimally, review the diff and run targeted validation. Avoid unrelated refactors, formatting and speculative features.
- Load context progressively: memory, handoff, file/symbol index, scoped source, then widen only when evidence requires it. Mark indexes incomplete and verify against source.
- Maintain `HANDOFF.md` with exactly these sections: Goal; Current state; Active files; Changes made; Failed attempts / pitfalls; Next steps; Other carry-over details. Never place secrets in handoff or memory.
- Maintain `PROJECT_MAP.md`, `RUNNING.md`, `.codex/PROJECT_MEMORY.md`, and optional stable decisions/skills registry without redundant process. Do not claim unverified production commands work.
- Route the preferred skills documented in the references only after confirming that they are available. Never install untrusted skills or scripts automatically.
- Escalate actual business tradeoffs, destructive or irreversible operations, security or production impact, external charges, and missing permissions. Continue independent safe work.
- Use risk-proportional QA and authorized, non-destructive dynamic testing on explicitly scoped targets. Report pass/fail/not run accurately.
- Prefer existing compatible containers for web applications, minimal privileges, safe secret handling, and verified operational instructions.

## Utilities and verification

- Resolve the intended non-root POSIX host user or original sudo caller on first run. Reject ambiguous root-only sessions. Record username/group, numeric UID/GID and host in ignored local state; guard later writes and make ownership audit-only. Do not use unsafe recursive `chown` or `chmod 777`.
- Provide idempotent init, bounded file/symbol indexing, handoff updates, status and ownership audit with explicit errors, path-traversal protection and no writes outside project root. Exclude binary, generated, `.git`, vendor and `node_modules` content.
- Provide `code_index.py` as an offline incremental SQLite navigation index: SHA-256 change detection, bounded source discovery, conservative Python AST extraction, heuristic non-Python declarations and direct-import hints, plus `build`, `find`, `impact` and `stats`. Do not claim complete semantic cross-language analysis.
- Handoff updates must target one of the seven known sections, preserve unrelated content and reject empty or oversized entries.
- CI must check Python compilation, skill metadata/references and unit tests with least-privilege workflow permissions. Include a sample fixture.
- Measure first, unchanged incremental and one-file-changed builds on a throwaway fixture. Report observed timings and changed counts without converting them to token-savings claims.
- Document global (`~/.agents/skills/`) and per-repository (`.agents/skills/`) installation, `$fady-autonomous-engineering` invocation, limits and verification commands.

## Delivery boundary

Show the exact proposed files and validation evidence. Keep work ready for review; never push or publish without the owner's explicit approval.

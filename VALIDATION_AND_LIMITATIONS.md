# Validation results and outstanding operational dependencies

## Validation completed (2026-11-23)
- Project initialization, ownership resolution, incremental indexing, and handoff tests: **20 passed** under a non-root test account.
- Skill metadata/reference validation: passed.
- Skill-creator validator: passed.
- Code-index fixture: 240 Python source files, no external dependencies.
  - First build: 240 changed, 0 unchanged; 0.4114 seconds.
  - Second build: 0 changed, 240 unchanged; 0.0188 seconds.
  - Third build (one file modified): 1 changed, 239 unchanged; 0.0171 seconds.
- These are illustrative single-run timings on a synthetic fixture, not a robust performance benchmark. They do **not** quantify Codex context or token savings.

## Implemented
- Incremental content-hash change detection; exact Python AST declarations and import collection; heuristic cross-language declarations and relative JS/TS imports.
- Path/symbol substring lookup, limited direct-import impact suggestions, and stale-entry cleanup.
- Idempotent project document initialization, status and file-index tools.
- Seven-section handoff append helper, preserving existing sections.
- GitHub Actions validation for script syntax, tests and metadata.
- First-run host user/group detection and locally persisted UID/GID; subsequent write guards; read-only ownership audit.

## Unfinished by design: depends on your actual environment
- Real Codex subagent spawning, concurrency and permissions: require runtime support and explicit configuration.
- `superpowers`, `gstack`, `graphify`, `rea`, `find-skills`, `codex-security`, UI/UX skills: verify availability and follow their actual instructions before use.
- Full cross-language semantic or call graphs: require project-aware LSP/compiler or other suitable tool; heuristic imports are not complete.
- Production Docker runtime, database access, secret management, test targets and authorized dynamic pentesting: require a real project and scope.
- Host UID/GID ownership cannot be guaranteed from a Git checkout or archive. First-run init intentionally fails in an ambiguous root-only session; run as the intended non-root user on the target host and audit after deployment.
- Remote GitHub publication: no destination repository was supplied or selected; ready-to-push package only.

## Release caution
Do not grant agents blanket write/execute permissions or let them run unknown scripts autonomously. Use read-only indexing and review irreversible actions. Do not interpret passing unit tests as proof of application security.

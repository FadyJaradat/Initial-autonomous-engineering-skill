# Context, index, and continuity

## Entry and recovery
1. Inspect user task, applicable instructions, `HANDOFF.md`, and stable `.codex/PROJECT_MEMORY.md` if they exist. Do not create state docs for simple standalone Q&A.
2. Inspect `git status --short`, then relevant `PROJECT_MAP.md`, `.codex/FILE_INDEX.json`, `.codex/SYMBOL_INDEX.json` if needed.
3. Search by filename or symbol (`rg --files`, `rg -n` within limited paths); read narrowly scoped source and its tests. Never trust stale indexes over source.
4. Use progressive expansion: summary -> file index -> symbol index -> relevant code -> direct callers/tests -> wider inspection only on evidence.

## Initialization
Run `project_tools.py init --root <repo>` only when authorized to modify the target repository. It creates missing docs from templates without overwriting existing files. Do not populate guesses; mark unknown items as unverified. For new projects, record technology stack and working commands only after checking.

## Mapping
Run `project_tools.py index` on bootstrap or after code changes that affect navigation. It uses `git ls-files` where possible, filters binary/generated files, and records file metadata and Python AST symbols; it is not a semantic cross-language index. Prefer available language servers, graphify, or repo-specific tools for deeper dependency/call graphs. Do not install new indexers without evaluating risk and maintenance cost. Invalidate based on changed file content/diff; refresh affected info where possible; do not repeatedly print index JSON into conversation.

## Memory contract
- `HANDOFF.md`: immediate objective, state, active files, changes, failed paths, next action, carry-over details. Keep current, concise and evidence-based; archive history as needed.
- `.codex/PROJECT_MEMORY.md`: stable stack, architecture, standards, environment constraints; change only when a durable fact changes.
- `PROJECT_MAP.md`: meaningful folders, entry points, subsystem relationships; don't describe generated folders.
- `RUNNING.md`: simplest *verified* dev and production commands; label unknowns unverified.
- `.codex/DECISIONS.md`: nontrivial choices and rationale, no exhaustive trivia.

Do not write credentials, user data, API tokens or private keys into docs, indexes or logs. Generated indexes are optional; the project works without them.

## Compact delegation
Pass agents: objective, scoped files/symbols, acceptance criteria, constraints, output location. Expect short reports: `STATUS / EVIDENCE / FILES / RISKS / NEXT`. Put long logs in files not messages. Summarize useful findings to handoff before compaction.

## Incremental repository navigation (v2)
Use `scripts/code_index.py build` after bootstrapping and after source changes. Source-code hashes avoid reparsing unchanged files. `find --query <partial-symbol-or-path>` returns small, bounded results. `impact --path <relative-file>` finds likely direct importers only. Validate against source and broader search before claiming completeness. The SQLite database is disposable and ignored by Git; rebuilding it never changes the application. Run `stats` to measure stored records. `build` returns the number of changed/unchanged/deleted files and runtime; this is not a token benchmark. The JavaScript/TypeScript and other non-Python symbol patterns are heuristic, not an LSP, compiler or semantic analyzer. Prefer an already-installed LSP, `graphify`, or project-native code intelligence for real cross-language call graphs.

## Handoff helper
Use `scripts/handoff.py --section '<one of seven section titles>' --entry '<verified short note>' --root .` to append entries without replacing other sections. Preserve manually edited handoff structure; abort if the requested section is missing. Do not log secrets or large command outputs.

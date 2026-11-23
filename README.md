# Fady Autonomous Engineering — reusable Codex skill

A repository-ready, **one-skill** autonomous engineering workflow for Codex. Includes progressive-loaded guidance, safe project bootstrap, lightweight codebase indexing, handoff updates and ownership auditing. A skill does **not** itself provision agents, tools, credentials, or background execution; it orchestrates what the Codex runtime actually supports.

## Use in a project

Copy `.agents/skills/fady-autonomous-engineering/` into your repository and optionally copy the root `AGENTS.md` into the project root. Keep the `.agents` folder committed. Open Codex in the project and invoke:

```text
$fady-autonomous-engineering Initialize this project, create only missing state docs, index source files, and report any deployment or ownership gaps.
```

Or use this repo as your central skills repository and copy/symlink the skill into `~/.agents/skills/fady-autonomous-engineering/` for global availability. Symlink support depends on host environment.

To run the deterministic tools without Codex:

```bash
python3 .agents/skills/fady-autonomous-engineering/scripts/project_tools.py owner --root .
python3 .agents/skills/fady-autonomous-engineering/scripts/project_tools.py init --root .
python3 .agents/skills/fady-autonomous-engineering/scripts/project_tools.py index --root .
python3 .agents/skills/fady-autonomous-engineering/scripts/project_tools.py status --root .
python3 .agents/skills/fady-autonomous-engineering/scripts/project_tools.py ownership --root .
```

`init` never overwrites existing documents. `index` writes lightweight file and Python symbol maps, not semantic/complete dependency graphs. `owner` discovers the current host account; `init` persists it as an ignored, host-specific record and writes `.codex/cache/owner.env` containing PUID/PGID. `ownership` only audits ownership; it does not change it. Generated state belongs in `.codex/` (normally commit stable memory and decisions; ignore machine-specific indexes if desired).

## Contents

- `SKILL.md`: concise control plane.
- `references/`: optional stage-specific guidance.
- `scripts/project_tools.py`: zero-dependency, stdlib-only project init/index/status/ownership audit.
- `assets/templates/`: templates copied only when missing.
- `MASTER_CREATION_PROMPT.md`: full one-shot prompt to regenerate/enhance the skill in Codex.

## Security and compatibility

The skill never silently deploys to production, performs destructive actions, installs untrusted skills, or runs offensive testing outside documented authorization. Filesystem ownership belongs to the invoking non-root account on the target POSIX host; a Git checkout, Windows environment, or ZIP cannot guarantee it. Run ownership validation and configure UID/GID on the target host.

## Tests

```bash
python3 -m unittest discover -s .agents/skills/fady-autonomous-engineering/tests -v
```

## Incremental code navigation (recommended)

A local SQLite source index eliminates repeated full-file dumps. It uses **Python AST** and bounded, heuristic declarations/imports for common non-Python languages. This is **not** a complete semantic dependency map or a tokenizer-aware context manager.

```bash
SKILL=.agents/skills/fady-autonomous-engineering
python3 "$SKILL/scripts/code_index.py" build --root .
python3 "$SKILL/scripts/code_index.py" find --root . --query auth
python3 "$SKILL/scripts/code_index.py" impact --root . --path path/to/target.py
python3 "$SKILL/scripts/code_index.py" stats --root .
python3 "$SKILL/scripts/handoff.py" --root . --section 'Changes made' --entry 'Verified change summary'
```

The first build indexes source; subsequent builds use SHA-256 to skip unchanged source and remove deleted entries. Index data is saved in ignored `.codex/cache/code_index.sqlite3`. `.codex/cache/` is disposable. Avoid committing machine-specific state; keep stable memory and decisions in version control after reviewing for secrets.

### Automated validation
GitHub Actions runs syntax checks, the unit tests, and metadata/reference validation on pushes and pull requests. No credentials are needed for these tests. For local validation:

```bash
python3 -m unittest discover -s "$SKILL/tests" -v
python3 "$SKILL/scripts/validate_skill.py" --root "$SKILL"
```

### Limitations and production requirements
- A skill cannot itself start subagents or schedule background work; actual Codex runtime support is required.
- Import-impact suggestions are intentionally incomplete and must be verified with direct code inspection and project-aware tooling.
- Host the detected local non-root user/group ownership cannot be represented in Git or a ZIP. The included command is audit-only; target deployment must configure user/group and writable binds.
- No automatic production deployment, destructive changes or dynamic PT is included. These require an authorized project environment.
- Indexing reduces repeated parsing and narrows context selection, but **actual token savings have not been measured**. Benchmark on your own repositories before claiming a savings percentage.

## Local ownership (automatic on first run)

Run `init` as your ordinary non-root account on the **target host**, not as root and not inside a root-only build container. The skill records username, group, UID, GID and host in `.codex/LOCAL_OWNER.json` (Git-ignored). All subsequent write commands verify this record. Run `ownership` to inspect mismatches without changing permissions. When moving to another host, inspect and delete only this local record, then rerun `init` as that host's ordinary user. Do not commit local ownership records.

For bind-mounted writable Docker services use Compose `user: "${PUID}:${PGID}"` and use `docker compose --env-file .codex/cache/owner.env up -d --build` (when your actual project has a verified Compose configuration using `${PUID}:${PGID}`). For `.env`-based workflows, store those two values in an ignored local file. Run ownership audits on the host; a container process's UID is not a reliable way to infer the host login.

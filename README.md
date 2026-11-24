# Fady Autonomous Engineering

A portable Codex skill for scoped engineering work: repository bootstrap, surgical implementation, testing, security review, handoff and deployment planning. It coordinates runtime capabilities; it does not provision agents, credentials, background execution, or production access.

## Install

For one repository, copy `.agents/skills/fady-autonomous-engineering/` into that repository's `.agents/skills/` directory. For global availability, copy it to `~/.agents/skills/fady-autonomous-engineering/`. Keep the directory name and its contents intact. If Codex does not discover a newly copied skill, start a new session and invoke:

```text
$fady-autonomous-engineering Initialize this project, create only missing state docs, index source files, and report deployment or ownership gaps.
```

The optional root `AGENTS.md` supplies short project-wide defaults. Do not replace an existing `AGENTS.md` without reconciling its content.

## Local tools

Use Python 3.9 or newer and run as the intended non-root account on the target host. The `owner` command reports the current account or, when running under root, the original sudo caller; write commands refuse an effective root session to avoid root-owned files. `init` creates only missing templates, records host-specific UID/GID state under ignored `.codex/`, and prepares the Compose `PUID`/`PGID` file. Later writes verify that recorded identity. `ownership` only audits; it never changes permissions.

```bash
SKILL=.agents/skills/fady-autonomous-engineering
python3 "$SKILL/scripts/project_tools.py" owner --root .
python3 "$SKILL/scripts/project_tools.py" init --root .
python3 "$SKILL/scripts/code_index.py" build --root .
python3 "$SKILL/scripts/project_tools.py" status --root .
python3 "$SKILL/scripts/project_tools.py" ownership --root .
python3 "$SKILL/scripts/code_index.py" find --root . --query auth
python3 "$SKILL/scripts/code_index.py" impact --root . --path src/auth.py
python3 "$SKILL/scripts/code_index.py" stats --root .
python3 "$SKILL/scripts/handoff.py" --root . --section 'Changes made' --entry 'Verified change summary'
```

The offline SQLite index uses SHA-256 to skip unchanged source, Python AST for Python declarations/imports and conservative heuristics elsewhere. It excludes common generated/vendor directories, has bounded discovery, and reports import-level hints only. It is not a complete call graph, security scanner, or token-savings measure. Inspect source before decisions.

## Validate

```bash
SKILL=.agents/skills/fady-autonomous-engineering
python3 -m compileall -q "$SKILL/scripts" "$SKILL/tests"
python3 -m unittest discover -s "$SKILL/tests" -v
python3 "$SKILL/scripts/validate_skill.py" --root "$SKILL"
```

GitHub Actions runs the same checks on pushes and pull requests with read-only repository permissions. See [VALIDATION_AND_LIMITATIONS.md](VALIDATION_AND_LIMITATIONS.md) for this reconstruction's measured results and the distinct November 23 historical report.

## Safety and limits

- Optional skill names in the references are preferences; verify availability before use. Never install untrusted scripts automatically.
- Dynamic testing must be explicitly authorized and scoped. Production deployment and secret access require the actual project environment.
- Git and ZIP archives cannot guarantee POSIX ownership. Initialize and audit on the deployment host; ownership results do not repair mismatches.
- The sample fixture and unit tests validate utilities, not application security or Codex runtime discovery.

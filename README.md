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
python3 .agents/skills/fady-autonomous-engineering/scripts/project_tools.py init --root .
python3 .agents/skills/fady-autonomous-engineering/scripts/project_tools.py index --root .
python3 .agents/skills/fady-autonomous-engineering/scripts/project_tools.py status --root .
python3 .agents/skills/fady-autonomous-engineering/scripts/project_tools.py ownership --root .
```

`init` never overwrites existing documents. `index` writes lightweight file and Python symbol maps, not semantic/complete dependency graphs. `ownership` only audits ownership; it does not change it. Generated state belongs in `.codex/` (normally commit stable memory and decisions; ignore machine-specific indexes if desired).

## Contents

- `SKILL.md`: concise control plane.
- `references/`: optional stage-specific guidance.
- `scripts/project_tools.py`: zero-dependency, stdlib-only project init/index/status/ownership audit.
- `assets/templates/`: templates copied only when missing.
- `MASTER_CREATION_PROMPT.md`: full one-shot prompt to regenerate/enhance the skill in Codex.

## Security and compatibility

The skill never silently deploys to production, performs destructive actions, installs untrusted skills, or runs offensive testing outside documented authorization. Filesystem `fady:fady` ownership is a host-level requirement, not guaranteed on Windows, GitHub checkout or inside this ZIP. Run ownership validation and configure UID/GID on the target host.

## Tests

```bash
python3 -m unittest discover -s .agents/skills/fady-autonomous-engineering/tests -v
```

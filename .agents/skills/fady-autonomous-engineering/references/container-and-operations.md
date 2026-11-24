# Containers, operations and ownership

Prefer an existing working deployment. For new web apps, aim for reproducible Docker/Compose builds, non-root runtime, locked-down ports, healthchecks, env-based configuration, secrets outside images, volume persistence only when required, and clear production runbook. Do not add Kubernetes/service mesh without a real requirement.

`RUNNING.md` is the *verified* guide for prerequisites, configuration, startup, shutdown, logs, healthcheck, backups and recovery if applicable. `docker compose up -d --build` is an example, not a validated command until the repository has been inspected and executed.

Ownership mandate: project-generated files should belong to the intended local non-root host account. `project_tools.py owner` resolves that account (or the original sudo caller); `init` records username/group, UID/GID and host in ignored local state. Later write operations verify the record and refuse effective-root execution to avoid creating root-owned files. Audit via `project_tools.py ownership --root .`; the audit never changes permissions. A source checkout on GitHub/Windows cannot preserve POSIX ownership metadata; verify on the deployment host.

If the environment doesn't have the user/group, report this clearly; do not fabricate a successful audit. For rootless containers or unsupported host filesystems, document constraints and safe alternatives.

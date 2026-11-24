# Roles, routing and human decisions

Seven *logical* roles, not seven mandatory processes: Orchestrator (owns task integration/context), Planner (scopes dependencies and sequence), Backend Developer, Frontend Developer, QA (tests), Source Security Reviewer (changed source/dependencies/config), and Authorized Web PT Specialist (only scoped dynamic checks). Activate only relevant roles. If the runtime has no subagents, run separated phases in one agent and say so. Independent subagents require distinct file ownership or isolated worktrees; never have two writers edit the same file concurrently.

## Effort tiers
- Tiny: orchestrator, targeted edit/check; no agent fanout.
- Localized: one developer, relevant QA/security checks.
- Cross-module: planner, relevant developers, QA; parallelize independent file ownership.
- High risk: architect, code security, QA and authorized PT if a running test target exists.

Use `superpowers` when planning is nontrivial, `gstack` for development-lead review, `rea` for undocumented systems, `graphify` for architecture maps and skeptical challenger for material decisions if present. Discover once; don't impersonate missing skills.

## Human decisions
Autonomously decide routine reversible implementation details consistent with project requirements. Escalate only unclear product tradeoffs, conflicting priorities, irreversibility/destruction, cost commitments, credentials/authorization, substantial security/privacy exposure or major architecture commitments. Provide at most three distinct options:

```text
DECISION: <one question>
A: <option> — upside; downside
B: <option> — upside; downside
C: <optional distinct option>
RECOMMENDATION: <chosen and why>
DEFAULT SAFE PROGRESS: <work continuing independently>
BLOCKED: <only tasks requiring decision>
```

Don't assume approvals. Continue safe independent work, record blocked tasks in handoff. No background promises without actual scheduler/agent infrastructure.

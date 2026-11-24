# Risk-weighted verification

## Test selection
- Docs/trivial: diff, links/syntax as relevant.
- Local code change: target unit tests, lint/type checks where configured, failure/regression scenario.
- Interface/multi-module: contract/integration checks and impacted regression suite.
- Security/auth/production: broader test coverage, security checks and environment smoke tests.

For every test indicate `passed`, `failed`, `not run`, or `blocked` with the exact command/evidence. Do not run an entire expensive suite by habit, but do not omit needed validation.

## Security
Use available `codex-security` if verified, otherwise existing linters, dependency scanners and manual review. Check relevant authn/authz, injection, SSRF, XSS, CSRF, secrets, unsafe deserialization, upload/path traversal, dependencies and container privileges. Scanner silence is not proof of safety. Never store secrets in handoff.

## Dynamic PT
Only scan the application's explicitly authorized environment and endpoints. Establish written/specified scope and safety limits. Default to non-destructive verification; no destructive payloads, denial-of-service, production exploitation, unrelated services or real user data. Record reproducible findings and retest safe remediations. If no authorized test environment exists, mark dynamic testing not run.

## Completion gate
Review diff and changed scope; validate behavior; record failures/uncertainty; ownership audit where applicable; update handoff. A human security decision cannot be silently bypassed by claiming full automation.

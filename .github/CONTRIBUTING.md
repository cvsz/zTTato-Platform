# Contributing to ZeaZDev

Thank you for contributing to ZeaZDev projects.

This file provides organization-wide defaults. A repository-specific `CONTRIBUTING.md` always takes precedence when present.

## Contribution Principles

Contributions should be focused, reviewable, testable, secure, and easy to operate after merge.

Prefer changes that:

- solve one bounded problem at a time;
- preserve unrelated behavior;
- include regression coverage for changed behavior;
- make security boundaries explicit;
- avoid introducing unnecessary dependencies or architectural complexity;
- update documentation when contracts, configuration, deployment, or operations change;
- leave the repository in a coherent state.

## Before You Start

1. Read the target repository's `README.md`, `SECURITY.md`, issue templates, pull request template, and project-specific contribution rules.
2. Search existing issues and pull requests to avoid duplicate work.
3. For large, security-sensitive, or architecture-changing work, open an issue or proposal first unless maintainers have already defined the implementation slice.
4. Keep secrets, credentials, production data, and private customer information out of issues, commits, tests, logs, and screenshots.

## Development Workflow

A typical workflow is:

```text
Understand requirement
      ↓
Define bounded behavior
      ↓
Add/adjust tests where practical
      ↓
Implement the smallest correct change
      ↓
Run targeted checks
      ↓
Run required CI/security checks
      ↓
Update docs/evidence
      ↓
Open pull request
      ↓
Address review without widening scope
```

## Testing

Run the checks appropriate to the repository. These may include:

- formatting and linting;
- static type checks;
- unit tests;
- integration tests;
- service-backed database tests;
- security regression tests;
- installer or migration tests;
- end-to-end tests;
- container/build validation;
- supported-runtime compatibility checks.

For bug fixes, add a regression test whenever practical.

## Security Expectations

Do not weaken security gates to make a change pass.

Pay particular attention to:

- authentication and session boundaries;
- authorization and tenant isolation;
- input validation and output encoding;
- injection risks;
- CSRF/XSS protections;
- secrets handling;
- filesystem and workspace containment;
- privileged actions and auditability;
- dependency and supply-chain changes;
- network exposure and default-open services.

If a vulnerability is involved, follow `SECURITY.md` and avoid public disclosure until maintainers have had a reasonable opportunity to assess it.

## Pull Requests

A strong pull request explains:

- what problem is being solved;
- what changed;
- what intentionally did not change;
- security impact;
- compatibility or migration impact;
- tests executed;
- operational or deployment impact;
- screenshots or recordings for meaningful UI changes;
- follow-up work that remains out of scope.

Keep pull requests small enough to review confidently. Avoid mixing dependency upgrades, refactors, formatting churn, and feature work unless they are inseparable.

## Commit Quality

Use clear commit messages that describe intent. Do not commit generated secrets, local environment files, temporary debugging artifacts, or unrelated formatting changes.

## Documentation

Update documentation whenever a change affects:

- setup or prerequisites;
- environment variables;
- CLI/API behavior;
- permissions or security boundaries;
- deployment or infrastructure;
- migrations;
- backup/restore procedures;
- operational runbooks;
- supported versions or compatibility.

## Review

Review comments should be technical, actionable, and scoped to the change. When responding to feedback, verify the concern before modifying code and avoid unrelated cleanup.

## Licensing

By contributing, you agree that your contribution may be distributed under the license of the repository you are contributing to. Verify repository-specific licensing before submitting substantial third-party code.

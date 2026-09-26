# ZeaZDev Governance

This document defines a lightweight organization-wide governance baseline for ZeaZDev repositories. Individual repositories may define stricter or more specific rules.

## Decision Principles

Technical decisions should optimize for user value, security, correctness, operability, maintainability, and evidence rather than novelty or complexity.

Prefer decisions that are:

- explicit about constraints and trade-offs;
- reversible when uncertainty is high;
- supported by tests, measurements, standards, or reproducible evidence where practical;
- scoped to the problem being solved;
- documented when they affect architecture, security, APIs, operations, or long-term maintenance.

## Repository Ownership

Each active production-oriented repository should make ownership discoverable. Maintainers are responsible for keeping the repository's operational and security expectations understandable, including where applicable:

- supported branches and runtime versions;
- required CI/security gates;
- release process;
- deployment and rollback process;
- vulnerability reporting path;
- roadmap or execution source of truth;
- operational/runbook ownership.

## Change Classes

### Routine changes

Examples: documentation corrections, bounded bug fixes, low-risk maintenance, and compatible dependency updates.

These should still pass the repository's required evidence gates.

### Material changes

Examples: public API changes, persistent-data migrations, authentication/authorization changes, new network exposure, infrastructure changes, dependency/platform transitions, or substantial UI workflow changes.

Material changes should document impact, migration, rollback, test evidence, and operational implications.

### Security-critical changes

Examples: trust-boundary changes, privileged operations, tenant isolation, secret handling, filesystem containment, CI/CD credentials, or vulnerability remediation.

These require explicit security review and should not weaken existing controls merely to make implementation or CI easier.

## Merge Readiness

A change is merge-ready only when the evidence required by the target repository is satisfied. Depending on the project, this may include:

- required review complete;
- required CI checks green on the exact head commit;
- security checks green or explicitly dispositioned according to repository policy;
- regression coverage present;
- migration/rollback documented;
- user/operator documentation updated;
- unresolved review threads addressed;
- no known blocker hidden by retries or disabled checks.

A green status alone does not prove readiness if the relevant checks are missing.

## Scope Control

Avoid widening a bounded change during review unless a discovered issue is required for correctness or safety. Adjacent improvements should normally become follow-up work.

## Architecture Decisions

Significant architecture decisions should record:

- problem and constraints;
- considered options;
- selected approach and rationale;
- security implications;
- operational implications;
- migration path;
- known trade-offs and deferred work.

Repositories may use ADRs, design documents, RFCs, issues, or another documented mechanism.

## Release Maturity

Projects should avoid using labels such as "production ready" or "gold master" without evidence. Release maturity should reflect the actual state of required features, testing, security, migration safety, rollback, observability, backup/restore, and operational ownership.

## Incident and Security Learning

Material incidents and security findings should lead to durable improvements when practical: regression tests, safer defaults, detection, documentation, runbooks, policy checks, or architectural changes that reduce recurrence.

## Repository-Specific Precedence

If this file conflicts with an explicit policy in a target repository, the repository-specific policy governs that repository unless organization owners state otherwise.

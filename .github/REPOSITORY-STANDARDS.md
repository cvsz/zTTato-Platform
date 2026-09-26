# ZeaZDev Repository Standards

This document defines a practical maturity baseline for ZeaZDev repositories. Repository-specific requirements may be stricter.

## Required foundation

Production-oriented repositories should make ownership and operation discoverable through a clear README, license or explicit proprietary status, security policy, contribution guidance, tests, CI, dependency management, configuration examples without secrets, and release/operational documentation appropriate to the project.

## Default branch and changes

Use `main` unless a repository documents another canonical branch. Prefer pull requests for material changes. Protect release-critical branches with review and status-check requirements appropriate to repository risk. Do not weaken a required security or correctness gate merely to obtain a green merge.

## CI baseline

CI should run the checks that represent actual project risk: formatting/linting, type checks where applicable, unit/integration tests, build/package validation, security scanning, dependency review, compatibility matrices, migration checks, installer validation, and end-to-end tests where relevant. Required checks must be based on the exact head being merged.

## Security baseline

Apply least privilege to workflows and runtime identities. Keep secrets out of source and logs. Validate untrusted input server-side, enforce authorization server-side, use parameterized data access, maintain tenant/workspace boundaries, scan dependencies and source, and preserve auditable evidence for privileged or data-changing behavior.

Enable GitHub security features appropriate to repository visibility and plan, including secret scanning/push protection, Dependabot alerts/updates, dependency review, and code scanning when supported. Organization or repository administrators must enable platform settings; files in this repository document and automate what can be represented in source control but cannot substitute for administrative controls.

## Supply chain

Pin or deliberately version third-party actions and dependencies, review automated upgrades, generate SBOM/provenance for release artifacts where justified, and attest only artifacts whose exact build output and digest are known. Never claim provenance for a placeholder artifact.

## Releases

A production release should have a defined version, changelog/release notes, reproducible build path, migration impact, rollback/forward-fix plan, security evidence, test evidence, and operational owner. Release maturity labels must reflect evidence rather than aspiration.

## Operations

Services should expose useful health/readiness signals, structured logs, metrics/traces where justified, bounded retries/timeouts, graceful startup/shutdown, backup and restore procedures for durable data, migration safety, and incident/runbook guidance proportional to risk.

## AI and agentic systems

Treat model output as untrusted. Constrain tool access, filesystem/network access, secrets, data mutation, concurrency and execution time. Require explicit approval for high-impact actions where appropriate. Keep deterministic authorization and business rules outside model discretion. Maintain evaluation/regression evidence for important AI behavior.

## Documentation

Document setup, configuration, test commands, architecture/trust boundaries, deployment, rollback, troubleshooting, known limitations, and current incomplete work. Keep execution plans and checklists truthful: do not mark future phases complete because an earlier slice merged.

## Exceptions

A repository may intentionally omit a baseline item when it is not applicable. Document material exceptions and the reason so reviewers do not mistake absence for oversight.

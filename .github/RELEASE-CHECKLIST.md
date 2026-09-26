# Release Readiness Checklist

Use this as a baseline and adapt it to the repository's actual release model.

## Scope and version
- [ ] Release scope is explicit and bounded.
- [ ] Version/tag strategy is correct.
- [ ] Incomplete or deferred work is documented honestly.

## Correctness
- [ ] Required CI passes on the exact release head.
- [ ] Unit/integration/E2E evidence appropriate to the change passes.
- [ ] Supported runtime/platform matrix is verified.
- [ ] Install/upgrade/migration paths are validated when applicable.

## Security
- [ ] Required code/dependency/security scans pass or accepted findings are documented.
- [ ] No known credentials or secrets are included in source, artifacts, logs, examples, or images.
- [ ] Authentication, authorization, isolation, validation and privileged-action boundaries affected by the release were reviewed.
- [ ] New dependencies/actions have been reviewed.

## Data and recovery
- [ ] Schema/data migrations are reviewed and tested.
- [ ] Rollback or forward-fix behavior is defined.
- [ ] Backup/restore requirements are satisfied and recovery evidence is current when durable data is involved.

## Operations
- [ ] Health/readiness behavior is valid.
- [ ] Logging/metrics/tracing cover important failure modes.
- [ ] Configuration and secret requirements are documented.
- [ ] Runbooks/incident guidance are updated for changed operational behavior.

## Supply chain and artifacts
- [ ] Release artifacts are produced by the documented build path.
- [ ] Artifact checksums/digests are known where applicable.
- [ ] SBOM/provenance/attestation is generated where required and refers to the exact artifact.
- [ ] Third-party notices and licenses are preserved.

## Documentation and communication
- [ ] README/docs reflect user-visible or operational changes.
- [ ] Changelog/release notes describe behavior, migrations, breaking changes and known limitations.
- [ ] Support/security reporting paths remain valid.

## Final gate
- [ ] A maintainer has reviewed the exact release evidence.
- [ ] The release is classified accurately (experimental, development, RC, production-ready, etc.).
- [ ] Post-release verification and rollback owner are known.

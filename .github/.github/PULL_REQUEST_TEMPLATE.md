## Summary

Describe the bounded problem this pull request solves and the intended outcome.

## What changed

- 

## What intentionally did not change

- 

## Security impact

Describe any impact to authentication, authorization, tenant isolation, input validation, secrets, filesystem/network access, privileged operations, data mutation, or other trust boundaries. Write `None identified` when applicable.

## Compatibility / migration impact

Describe API, schema, configuration, dependency, runtime, deployment, or data-migration implications. Write `None` when applicable.

## Test evidence

List the exact checks run and their results.

```text
# command / workflow
# result
```

## Operational evidence

Note deployment, rollback, observability, health-check, backup/restore, performance, or runbook implications when applicable.

## UI evidence

For user-visible changes, include screenshots/recordings and responsive/accessibility notes where useful.

## Checklist

- [ ] Scope is bounded and unrelated cleanup was avoided.
- [ ] Tests cover the changed behavior where practical.
- [ ] Required lint/type/unit/integration/security checks pass.
- [ ] Security boundaries were reviewed and no gate was weakened merely to make CI pass.
- [ ] Documentation/configuration/examples were updated where required.
- [ ] Secrets, credentials, private data, and generated local artifacts are not included.
- [ ] Migration and rollback implications are documented where applicable.
- [ ] Follow-up work outside this PR is explicitly identified rather than silently bundled.

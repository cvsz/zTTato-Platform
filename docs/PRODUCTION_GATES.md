# Production Readiness Gates

Production-ready is an evidence claim, not a branch name.

Use independent gates. Passing one gate does not imply that every other gate has passed.

## Scope model

```text
Commerce Sources
      ↓
Product Ingestion
      ↓
Affiliate Core
      ↓
Content / Media
      ↓
Publishing Intent
      ↓
Distribution Providers
      ↓
TikTok Integration
```

See [ARCHITECTURE_BOUNDARIES.md](ARCHITECTURE_BOUNDARIES.md) and [AI_MASTER_PRODUCTION_PROMPT.md](AI_MASTER_PRODUCTION_PROMPT.md).

## Gate vocabulary

Use only:

- `PASS`
- `FAIL`
- `BLOCKED_EXTERNAL`
- `NOT_TESTED`
- `NOT_APPLICABLE`

Do not infer production readiness from source-code existence, documentation, mocked tests, or a successful local startup.

## P0 — application/platform

- [ ] Main branch ruleset/protection requires review and green CI/security checks.
- [ ] Production environment validation passes with HTTPS, PostgreSQL and persistent encryption key.
- [ ] Cloudflare/edge route exposes `/`, `/privacy-policy`, `/terms-of-service` and `/tiktok/callback` as required while admin surfaces remain protected.
- [ ] Legal entity, contact and postal address are real and counsel has reviewed public policies.
- [ ] PostgreSQL backup plus isolated restore is executed and timestamped.
- [ ] Media retention/deletion behavior is verified.
- [ ] Known-good container/image rollback is executed and timestamped.
- [ ] Token encryption key backup/rotation and incident procedure is tested.
- [ ] Monitoring/alerts cover 5xx, OAuth failures, TikTok upstream errors, disk/media capacity and DB health.
- [ ] No credentials are present in repository history or release artifacts.

## P0 — security

- [ ] Secret scan is clean or every finding is resolved/rotated and documented.
- [ ] OAuth state is cryptographically secure, short-lived and single-use.
- [ ] Access/refresh tokens are encrypted at rest and never logged or returned to clients.
- [ ] Tenant/resource authorization is enforced server-side.
- [ ] SSRF, CSRF, IDOR, path traversal, malicious upload and open redirect controls are tested.
- [ ] Rate limiting/resource exhaustion controls are verified.
- [ ] Production errors do not expose stack traces, credentials or internal secrets.

## P0 — Affiliate Core

Affiliate readiness is independent of TikTok readiness.

- [ ] Canonical Product model is source-neutral.
- [ ] Commerce provider IDs are not used as internal Product IDs.
- [ ] Product and Offer are separate concepts.
- [ ] Affiliate Links are independent of a specific distribution platform.
- [ ] Campaigns and content are platform-neutral.
- [ ] Media assets are reusable across distribution providers.
- [ ] Affiliate analytics are independent of TikTok availability.
- [ ] Affiliate functionality remains operational when TikTok is disabled/unavailable.
- [ ] Provider failures cannot corrupt Affiliate Core state.

## P0 — Commerce Integrations

- [ ] External provider APIs are isolated behind adapters/capability interfaces.
- [ ] External responses are validated and normalized before persistence.
- [ ] Pagination/cursors are handled correctly.
- [ ] Synchronization is idempotent.
- [ ] Retryable and permanent errors are distinguished.
- [ ] Provider outages do not delete or corrupt canonical products.
- [ ] Deduplication has deterministic identity rules.

## P0 — Distribution

- [ ] Publishing uses a provider-neutral contract.
- [ ] Publish jobs are tenant-scoped.
- [ ] Publishing is idempotent.
- [ ] Duplicate requests cannot create duplicate provider operations.
- [ ] Retry/backoff/rate-limit behavior is bounded and observable.
- [ ] Failed distribution jobs do not corrupt Affiliate Core entities.

## P0 — TikTok

- [ ] Exact TikTok redirect/domain/URL verification is complete.
- [ ] Requested scopes match actual application configuration.
- [ ] Real Sandbox E2E evidence covers every requested capability.
- [ ] `/dashboard` has been verified with a real authorized TikTok Sandbox account, not only mocked API tests.
- [ ] Creator information is queried immediately before Direct Post where required.
- [ ] Direct Post requires explicit current user consent.
- [ ] Upload/Draft flow is verified where applicable.
- [ ] Publishing status is persisted and reconciled.
- [ ] Duplicate-post reconciliation is exercised.
- [ ] Commercial disclosure and AI-generated-content behavior is reviewed against the current approved client configuration.
- [ ] TikTok production approval/audit is verified externally before claiming production Direct Post capability.

## P1 — database and operations

- [x] Add initial versioned Alembic migration and disable automatic `create_all` in production (still needs live PostgreSQL rehearsal).
- [ ] Isolated PostgreSQL migration and restore have been executed and timestamped.
- [ ] Scheduled cleanup removes expired browser/OAuth records and expired media.
- [ ] Content Posting webhooks are validated and authenticated where adopted.
- [ ] SBOM, container vulnerability scan and provenance evidence are produced for releases.
- [ ] Load/soak baseline is documented.
- [ ] Representative encrypted-token restore test is completed without exposing token values.

## CI acceptance

- [ ] CI runs on an assigned GitHub runner and all required jobs pass.
- [ ] Unit tests pass.
- [ ] Integration tests pass.
- [ ] Migration upgrade/downgrade/re-upgrade tests pass.
- [ ] Security/secret scans pass.
- [ ] Container build and scan pass.
- [ ] Production readiness tests fail closed when required evidence/configuration is absent.

## External blockers

External approval or infrastructure constraints must be recorded as `BLOCKED_EXTERNAL`, not hidden by changing source code or documentation.

Examples:

- TikTok app review/audit not completed.
- Production credentials unavailable.
- Real Sandbox account unavailable.
- Legal review incomplete.
- Production domain verification incomplete.
- Isolated infrastructure restore environment unavailable.

## Release rule

Do not close a gate from documentation alone.

Do not mark the overall repository `PRODUCTION_READY` while a critical P0 gate is `FAIL` or `NOT_TESTED`.

TikTok approval may remain `BLOCKED_EXTERNAL` while Affiliate Core is independently production-ready, provided the release does not claim unavailable TikTok capabilities.

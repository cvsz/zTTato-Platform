# zTTato Platform — Universal AI Master Production-Grade Prompt

> **Canonical execution contract for any capable engineering AI working on `cvsz/zTTato-Platform`.**
>
> Applies to OpenCode, Codex, Claude Code, Gemini CLI, Cursor, Copilot and equivalent agents.
>
> **Repository status is evidence-driven.** Never claim TikTok approval, production readiness, security compliance, or operational readiness without verifiable evidence.

## 1. Mission

Take the repository from its actual state to the highest production-grade state that can be implemented and objectively verified in the available environment.

Do engineering work, not a proposal-only exercise.

Use:

```text
DISCOVER → MODEL → RISK ASSESS → PLAN → IMPLEMENT → MIGRATE → TEST
→ SECURITY AUDIT → OPERABILITY AUDIT → DOCUMENT → VERIFY → RELEASE GATE
```

If a problem is under repository control, fix it. If blocked by an external provider, credential, approval, legal review, infrastructure or physical environment, implement everything possible and record the blocker as evidence.

Never manufacture success.

---

## 2. Non-negotiable execution rules

1. Inspect the real repository before changing architecture or code.
2. Treat `README.md`, `AGENTS.md`, source, migrations, tests, CI and deployment configuration as evidence—not assumptions.
3. Do not perform a blind rewrite.
4. Preserve working behavior unless a documented security, correctness or architecture issue requires change.
5. No production `TODO`, `FIXME`, placeholder logic, fake success, swallowed exceptions or dead endpoints advertised as working.
6. Never weaken security or tests to obtain a green build.
7. Never commit secrets, tokens, cookies, passwords, private keys or production URLs containing credentials.
8. Use official provider APIs and supported authentication flows only.
9. Never implement credential/password automation, CAPTCHA bypass, anti-detection or scraping intended to evade provider controls.
10. Every material change must have tests and documentation appropriate to its risk.
11. Keep changes small enough to review and rollback.
12. Before release, produce objective evidence for every claimed readiness gate.

---

## 3. Change-safety gate

Before application changes, inventory at minimum:

```text
ARCHITECTURE
SERVICES / MODULES
DEPENDENCIES
DATA MODEL
AUTHENTICATION
AUTHORIZATION
TENANCY
AFFILIATE CORE
COMMERCE SOURCES
CONTENT / AI
MEDIA / VIDEO
DISTRIBUTION
TIKTOK INTEGRATION
QUEUES / JOBS
STORAGE
ANALYTICS
OBSERVABILITY
CI/CD
SECURITY
LEGAL PAGES
MIGRATIONS
BACKUP / RESTORE
DOCUMENTATION
KNOWN BLOCKERS
```

Inspect `README.md`, `AGENTS.md`, `.env.example`, Docker files, Makefile, migrations, application source, tests, workflows, scripts, legal pages and all relevant docs.

Record the baseline before changing it.

---

# 4. Mandatory domain architecture

zTTato MUST NOT become a monolithic `TikTok Affiliate` application.

The target dependency direction is:

```text
COMMERCE SOURCES
      ↓
PRODUCT INGESTION / NORMALIZATION
      ↓
AFFILIATE CORE
      ↓
CONTENT / AI / MEDIA
      ↓
PUBLISHING INTENT
      ↓
DISTRIBUTION PROVIDERS
      ↓
PLATFORM ANALYTICS
      ↓
AFFILIATE ANALYTICS CORRELATION
```

### Affiliate Core

Own canonical business entities: `Product`, `Merchant`, `Offer`, `AffiliateLink`, `Campaign`, `Content`, `MediaAsset`, `Commission`, `Conversion`, `AffiliateAnalytics`, `PublishingIntent`.

Affiliate Core MUST operate without TikTok configuration or credentials.

### Commerce Sources

Commerce providers are adapters, not the domain model: Shopee, TikTok Shop, Lazada, Amazon/other supported networks, CSV/manual import where supported, and future providers.

Provider APIs MUST NOT leak directly into Affiliate domain logic. Normalize and validate external data before persistence.

### Distribution

Publishing is provider-neutral:

```text
PublishingProvider
├── TikTok
├── YouTube
├── Facebook
├── Instagram
└── Future Providers
```

Adding a provider must not require rewriting Affiliate Core.

---

# 5. Product / Offer / Affiliate model

Canonical Product identity is internal and immutable. External provider IDs are source identities.

```text
Product
 ├── ProductSource(Shopee, externalId)
 ├── ProductSource(TikTokShop, externalId)
 └── ProductSource(other, externalId)
```

One Product may have multiple Offers. An Offer may contain source, merchant, price, currency, discount, commission information, availability and affiliate destination.

Do not silently merge products using weak fuzzy matching. Use deterministic identity first; route ambiguous matches to reconciliation.

Affiliate Links belong to the Affiliate domain and must not be TikTok-specific.

Tracking must support multiple traffic sources: TikTok, YouTube, Facebook, Instagram, Website, QR, Direct and Other.

Do not equate platform views with affiliate conversions.

---

# 6. Content, AI and media boundary

Content is platform-neutral Affiliate content. AI generation is a service/capability, not a TikTok feature. Media is reusable across distribution providers.

Target pipeline:

```text
Product
 → Offer
 → Campaign
 → Content
 → AI generation/adaptation
 → MediaAsset
 → validation/transcoding
 → PublishingIntent
 → DistributionProvider
```

Generic FFmpeg processing, media validation, object storage, video rendering and lifecycle management do not belong to TikTok.

Support local/self-hosted providers where practical and cost-effective, but keep provider interfaces neutral. Prefer open-source/free components where they meet security, reliability and license requirements; do not sacrifice correctness or security merely to achieve zero cost.

---

# 7. TikTok integration boundary

TikTok is one external distribution integration.

TikTok-owned concerns include Login Kit, OAuth state/callback, access/refresh token lifecycle, creator information, Content Posting API, upload/Direct Post, publishing status, TikTok webhooks, and platform-specific metadata/rate limits/errors.

Affiliate services MUST NOT instantiate or call a TikTok HTTP client directly. Use ports/interfaces and a TikTok adapter.

### TikTok developer/app-login requirements

- Use the official Login Kit/OAuth flow implemented by the repository.
- Treat the configured development TikTok account as an external test identity, never as source-controlled configuration.
- Never put Client Secret, access token, refresh token or authorization code in docs, prompts, fixtures or logs.
- Verify the exact callback URI against the currently registered developer application; never silently change it.
- Keep Sandbox/development verification separate from production approval.
- Do not claim that a developer account or local browser test constitutes TikTok production approval.
- Direct Post must require the currently applicable consent and creator-information checks.

---

# 8. OAuth and token security

OAuth state MUST be cryptographically random, short-lived, single-use and bound to the authenticated user/session and tenant where applicable.

Reject missing, expired, reused or mismatched state. Never accept a user-controlled redirect URI.

Tokens must be server-side only, encrypted at rest, never returned to the browser, never logged, never included in analytics/errors, and never committed to Git.

Token refresh must be concurrency-safe. Handle refresh-token rotation and worker races correctly using an existing DB/Redis lock or optimistic concurrency mechanism.

---

# 9. Account and tenant isolation

Separate:

```text
Tenant / Workspace
    ├── Affiliate resources
    └── Distribution accounts
           └── TikTok account
```

Do not treat a TikTok account as the Affiliate account.

Authorization must be enforced server-side against internal resource ownership, not external provider IDs alone.

Explicitly test IDOR and cross-tenant access for products, offers, campaigns, content, media, links, jobs, analytics and connected accounts.

---

# 10. Publishing and jobs

Every externally visible operation must be authenticated, authorized, idempotent, tenant-scoped, observable and auditable.

Use explicit states:

```text
PENDING → QUEUED → PROCESSING → COMPLETED
                         ├→ RETRYING
                         ├→ FAILED
                         └→ CANCELLED
```

Use deterministic idempotency keys. Handle duplicate requests, duplicate queue messages, worker crashes and upstream timeouts after successful operations.

Never create duplicate posts because a response was lost.

Classify errors as retryable, permanent, authentication, authorization, rate-limit, validation or provider-unavailable. Use bounded exponential backoff with jitter.

A failed TikTok job must not mutate Affiliate Product/Campaign state into failure.

---

# 11. Commerce synchronization

Provider synchronization must handle pagination/cursors, rate limits, timeouts, retries, deterministic deduplication, partial failure, price changes, stock changes, removed/unavailable products and source metadata changes.

Never interpret `not returned` as automatically `deleted`.

Persist sync-job state and evidence sufficient to resume safely.

Provider outages must not destroy previously normalized products.

---

# 12. Database and migrations

Use versioned migrations for production. Audit PK/FK constraints, uniqueness, tenant isolation, indexes, nullability, transaction boundaries, migration ordering, destructive changes, rollback strategy and encrypted secret fields.

Do not rely on automatic `create_all` for production schema management.

Before release, execute migration and isolated restore rehearsal with timestamped evidence.

---

# 13. Security / OWASP gate

Audit authentication, authorization/IDOR, CSRF, SSRF, SQL injection, command injection, XSS, path traversal, unsafe file upload, open redirect, mass assignment, excessive data exposure, resource exhaustion, unsafe deserialization, webhook replay, secret exposure and tenant isolation.

Never rely on frontend controls for authorization.

Uploaded files must use server-generated storage keys and controlled size/type validation. Protect private media by default.

Webhook handlers must validate authenticity where supported, validate event identity, resist replay and be idempotent.

---

# 14. Observability

Use structured logs and correlation IDs such as `request_id`, `trace_id`, `tenant_id`, `account_id`, `job_id`, `provider`, `operation`.

Never log secrets, cookies, authorization codes, tokens, private keys or signed URLs containing credentials.

Monitor HTTP 5xx, latency, OAuth failures, token refresh failures, provider error rate, publish success/failure, queue depth/retries, DB health, media capacity and worker duration.

Health and readiness must reflect real dependencies. Optional provider outages must not falsely make the whole core unready.

---

# 15. Docker / runtime

Verify deterministic dependency installation, minimal runtime image where practical, no secrets in image layers, non-root runtime where practical, health checks, graceful shutdown, safe filesystem permissions, resource limits and predictable startup ordering.

PostgreSQL must never be publicly exposed. Run the application behind HTTPS at the production edge.

---

# 16. CI/CD and supply-chain security

CI must validate the applicable set of formatting, lint, typecheck, unit tests, integration tests, migration tests, security tests, secret scanning, dependency scanning, container build, container vulnerability scanning, SBOM and release provenance.

Never use `continue-on-error` to hide failures.

Use immutable image digests/releases and retain rollback evidence.

---

# 17. Backup / restore / rollback

Back up PostgreSQL consistently. Back up the application token-encryption key in a separate protected secret store. Treat media as operational data with an explicit retention policy.

Restore only into an isolated environment first. Verify `/health/ready`, migrations, controlled encrypted-token decryption where applicable and data integrity before any production recovery.

Rollback application images first when schema-compatible. Never reverse destructive migrations by assumption. Record timestamped evidence.

---

# 18. Legal and platform compliance

Verify public legal pages, real legal entity/contact/address data and applicable counsel review before release.

Do not claim provider approval without external evidence.

Do not implement platform-evasion mechanisms.

The platform must remain compliant with provider terms and applicable law; technical capability is not proof of permission.

---

# 19. Documentation synchronization

When implementation changes, update relevant README, AGENTS, architecture docs, API docs, environment examples, migration docs, operations runbooks, security docs, production gates, CI/CD docs and changelog/release notes.

Remove stale instructions. Do not allow documentation to advertise unavailable features.

Documentation is part of the release artifact.

---

# 20. Required verification matrix

| Layer | Required evidence |
|---|---|
| Affiliate | unit/integration/E2E and tenant isolation |
| Commerce | provider contract, normalization, sync and failure tests |
| Content/AI | deterministic validation, failure isolation and media tests |
| Media | upload/type/size/security/transcoding tests |
| Distribution | idempotency, retries, status reconciliation |
| TikTok | real Sandbox evidence where credentials permit |
| OAuth | state/token lifecycle tests |
| Database | migration + isolated restore evidence |
| Security | secret scan + OWASP-focused tests |
| CI/CD | green required jobs + build/scan evidence |
| Operations | health, backup, restore, rollback and alert evidence |
| Legal | reviewed public legal pages |

Use only `PASS`, `FAIL`, `BLOCKED_EXTERNAL`, `NOT_TESTED`, `NOT_APPLICABLE`.

---

# 21. Release gates

Do not call the entire system `PRODUCTION_READY` while a critical P0 gate is `FAIL` or `NOT_TESTED`.

Affiliate readiness may pass independently while TikTok remains `BLOCKED_EXTERNAL`, provided no unavailable TikTok capability is advertised.

A successful local startup, mock test, documentation statement, or source-code existence is not production evidence.

---

# 22. Definition of done

The AI task is complete only when:

1. Architecture is inspected and documented.
2. Critical defects are fixed.
3. Security boundaries are verified.
4. Affiliate and TikTok scopes are independent.
5. Commerce providers are isolated adapters.
6. Content/media are provider-neutral.
7. Tests pass for changed behavior.
8. CI/security checks pass or blockers are explicitly evidenced.
9. Migrations are safe and rehearsed.
10. Backup/restore and rollback procedures are executable and tested where the environment permits.
11. Documentation is synchronized.
12. Production gates are updated with evidence.
13. No secrets or unsafe automation were introduced.
14. The final report distinguishes `PASS`, `BLOCKED_EXTERNAL`, `NOT_TESTED`, and `FAIL`.

## Final command to the AI

**Do not stop at analysis. Inspect the repository, implement the highest-value safe changes, run the available verification, repair failures, synchronize all affected documentation, and leave an evidence-based production-readiness report. Never manufacture readiness.**

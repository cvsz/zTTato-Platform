# Agent System Rules

## Canonical contract

Before modifying this repository, read and follow:

1. `docs/AI_MASTER_PRODUCTION_PROMPT.md`
2. `docs/ARCHITECTURE_BOUNDARIES.md`
3. `docs/SCOPE_AND_RESPONSIBILITY_MATRIX.md`
4. `docs/PRODUCTION_GATES.md`

These documents define the canonical production-grade architecture and execution rules.

## Engineering rules

- Explain developer-facing work primarily in Thai; keep code, commands, variables, protocol names and API routes in English.
- Inspect the real repository before changing it. Do not assume a feature exists because a prompt says it should.
- Do not perform blind rewrites.
- Never copy tokens, cookies, personal data or secrets from source repositories.
- Never commit credentials or secret values, including development TikTok credentials.
- Use official TikTok OAuth/Login Kit and Content Posting API rather than browser-based username/password automation.
- Do not implement scraping, CAPTCHA bypass, anti-detection or provider-control evasion.
- Affiliate Core, Commerce Sources, Content/Media and Distribution/TikTok must remain separate bounded contexts.
- Affiliate functionality must remain usable without TikTok.
- Commerce provider APIs must remain behind adapters and normalized into internal domain models.
- Require current creator-info and explicit consent for every direct post where required; preserve idempotency.
- Token handling must be encrypted at rest, server-side only, concurrency-safe and absent from logs.
- Validate tenant ownership server-side for every protected resource.
- Every external operation must have appropriate timeout, error classification, retry/idempotency and observability behavior.
- No production `TODO`, `FIXME`, fake success, swallowed exception or mock provider enabled accidentally in production.
- Do not weaken security checks or tests to make CI pass.

## Production claims

Never claim production readiness without the evidence required by `docs/PRODUCTION_GATES.md`.

Never claim TikTok production approval from source code, mocks, local browser tests or Sandbox activity alone.

External blockers must be recorded as `BLOCKED_EXTERNAL` rather than hidden.

## Authorization boundary

Do not submit the TikTok app for review, rotate production credentials, publish externally, change registered production redirects, or deploy to production without explicit authorization and the required evidence gates.

# zTTato Platform — Architecture Boundaries

## Purpose

This is the mandatory architecture boundary for humans and AI agents.

zTTato is **not** a monolithic TikTok Affiliate application. It is a platform composed of independent bounded contexts:

```text
Commerce Sources
      ↓
Product Ingestion / Normalization
      ↓
Affiliate Core
      ↓
Content / AI / Media
      ↓
Publishing Intent
      ↓
Distribution Providers
      ↓
Platform Analytics
      ↓
Affiliate Analytics correlation
```

See [SCOPE_AND_RESPONSIBILITY_MATRIX.md](SCOPE_AND_RESPONSIBILITY_MATRIX.md) for the ownership matrix and [AI_MASTER_PRODUCTION_PROMPT.md](AI_MASTER_PRODUCTION_PROMPT.md) for the execution contract.

## Affiliate Core

Owns the canonical business model:

- Product
- Merchant
- Offer
- Affiliate Link
- Campaign
- Content
- Media Asset
- Commission
- Conversion
- Affiliate Analytics
- Publishing Intent

Affiliate Core MUST work without TikTok configuration or credentials.

## Commerce Integrations

Commerce providers such as Shopee, TikTok Shop, Lazada, Amazon/other networks and future sources are external adapters.

Provider schemas MUST NOT become canonical domain models.

Normalize and validate external data before persistence. Keep provider identity separate from internal identity.

```text
Product
 ├── ProductSource(Shopee, externalId)
 ├── ProductSource(TikTokShop, externalId)
 └── ProductSource(other, externalId)
```

A provider outage must not corrupt or delete already normalized products.

## Content / AI / Media

Content and media are platform-neutral.

```text
Product
 → Offer
 → Campaign
 → Content
 → AI generation/adaptation
 → MediaAsset
 → validation/transcoding
 → PublishingIntent
```

AI providers, FFmpeg, rendering, object storage and generic media validation are not TikTok responsibilities.

Local/self-hosted/open-source components are preferred when they meet security, reliability, performance and licensing requirements, but zero-cost is not a justification for insecure or unreliable infrastructure.

## Distribution Integrations

Publishing MUST use a provider-neutral boundary:

```text
PublishingProvider
├── TikTok
├── YouTube
├── Facebook
├── Instagram
└── Future Providers
```

Adding a distribution provider must not require rewriting Affiliate Core.

## TikTok Integration

TikTok owns only platform-specific concerns:

- Login Kit
- OAuth state and callback
- access/refresh token lifecycle
- creator information
- Content Posting API
- upload / Direct Post
- publishing status
- TikTok webhooks
- platform-specific metadata, limits and errors

TikTok credentials MUST remain inside the TikTok integration boundary.

Affiliate services MUST NOT directly call TikTok APIs.

Use provider interfaces/ports and a dedicated adapter.

The configured development TikTok account is an external test identity only. Never place its credentials or tokens in source control, prompts or fixtures.

## Account and Tenant Model

```text
Tenant / Workspace
├── Affiliate resources
│   ├── Products
│   ├── Offers
│   ├── Campaigns
│   ├── Content
│   └── Affiliate Links
└── Distribution Accounts
    ├── TikTok
    ├── YouTube
    ├── Facebook
    └── Future providers
```

A TikTok account is not an Affiliate account.

Authorization must use internal tenant/resource ownership rather than external provider IDs alone.

## Analytics

### Affiliate metrics

- clicks
- conversions
- commission
- revenue
- ROI
- campaign/product performance

### Distribution metrics

- views
- likes
- comments
- shares
- watch time
- follower changes
- platform publishing status

Distribution metrics may be correlated to Affiliate campaigns/content through stable internal IDs, but must not be treated as equivalent business metrics.

## Failure Isolation

A TikTok outage MUST NOT make Affiliate Core unavailable.

A commerce-provider outage MUST NOT invalidate existing canonical products.

An AI or media-provider outage MUST NOT corrupt source campaign state.

A failed publishing operation affects the publishing job, not the source Product or Campaign.

## Security Isolation

Never expose outside the owning integration boundary:

- client secrets
- access tokens
- refresh tokens
- OAuth authorization codes
- cookies/session credentials
- signed upload URLs containing credentials
- commerce API credentials
- AI provider keys

## Architecture Acceptance

The boundary passes only when:

- Affiliate works independently of TikTok.
- Commerce providers are adapters.
- TikTok is a distribution integration.
- Provider schemas do not leak into the domain layer.
- Publishing is provider-neutral.
- Product identity is source-neutral.
- Product and Offer are separate.
- Content and Media are platform-neutral.
- Provider failures are isolated.
- Tenant authorization is enforced server-side.
- Integration secrets are isolated.
- Adding a commerce provider does not require rewriting Affiliate Core.
- Adding a distribution provider does not require rewriting Affiliate Core.

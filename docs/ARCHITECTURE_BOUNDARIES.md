# zTTato Platform — Architecture Boundaries

## Purpose

This document defines the mandatory domain boundaries for zTTato Platform.

The platform is not a monolithic TikTok application. It is a business platform with independent Affiliate Core, Commerce Integrations, Content/Media, Distribution Integrations, and Analytics capabilities.

## Canonical Dependency Direction

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
Platform Analytics
      ↓
Affiliate Analytics correlation
```

## Affiliate Core

Owns:

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

External commerce providers include Shopee, TikTok Shop, Lazada, and future providers.

They provide source data through provider adapters.

Provider schemas MUST NOT become the canonical business model.

A source product is identified by the provider and external ID; the internal Product has its own immutable identity.

## Distribution Integrations

TikTok is a distribution provider.

The platform MUST use a provider-neutral publishing boundary so additional providers can be added without rewriting Affiliate Core.

Conceptually:

```text
PublishingProvider
├── TikTok
├── YouTube
├── Facebook
├── Instagram
└── Future Providers
```

## TikTok Integration

TikTok owns only platform-specific concerns:

- Login Kit
- OAuth transactions
- token lifecycle
- creator information
- Content Posting API
- upload/direct-post operations
- platform-specific publishing status
- platform-specific webhooks
- platform-specific metadata

TikTok credentials MUST remain inside the TikTok integration boundary.

Affiliate services MUST NOT directly call TikTok APIs.

## Content / Media

Content and media are platform-neutral.

The canonical pipeline is:

```text
Product
 → Offer
 → Campaign
 → Content
 → MediaAsset
 → PublishingIntent
 → DistributionProvider
```

FFmpeg, media validation, storage, and generic video generation do not belong to TikTok unless an adapter needs a platform-specific transformation.

## Analytics

Keep separate dimensions:

### Affiliate

- clicks
- conversions
- commission
- revenue
- ROI
- campaign/product performance

### Distribution

- views
- likes
- comments
- shares
- watch time
- follower changes
- platform publishing status

Distribution metrics may be correlated to Affiliate campaigns/content through stable internal IDs, but one must not be treated as the other.

## Failure Isolation

A TikTok outage MUST NOT make Affiliate Core unavailable.

A commerce-provider outage MUST NOT invalidate already normalized products.

A failed publishing operation must affect the publishing job, not the source Product or Campaign.

## Security Isolation

Never expose the following outside the provider integration that owns them:

- client secrets
- access tokens
- refresh tokens
- OAuth authorization codes
- session credentials
- signed upload URLs containing credentials

## Production Acceptance

The architecture passes this boundary gate only when:

- Affiliate works independently of TikTok.
- Commerce providers are adapters.
- TikTok is a distribution integration.
- Provider-specific API schemas do not leak into the domain layer.
- Publishing is provider-neutral.
- Product identity is source-neutral.
- Offer is separate from Product.
- Content and Media are platform-neutral.
- Provider failures are isolated.
- Tenant authorization is enforced at the internal resource level.
- Adding a new commerce provider does not require rewriting Affiliate Core.
- Adding a new distribution provider does not require rewriting Affiliate Core.

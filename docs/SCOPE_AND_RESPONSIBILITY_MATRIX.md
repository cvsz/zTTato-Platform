# zTTato Platform — Scope & Responsibility Matrix

This document is the canonical boundary reference for all human and AI contributors.

## 1. Core rule

**Affiliate is the business core. TikTok is a distribution integration. Commerce platforms are product/offer sources. Content and media are reusable platform capabilities.**

Never reverse these dependencies.

## 2. Responsibility matrix

| Capability | Owner | Must work without TikTok? | Provider-specific data allowed? |
|---|---|---:|---:|
| Product catalog | Affiliate Core | Yes | Only in source metadata |
| Merchant | Affiliate Core | Yes | Source references allowed |
| Offer | Affiliate Core | Yes | Yes, behind source boundary |
| Affiliate link | Affiliate Core | Yes | Provider ID/URL as metadata |
| Campaign | Affiliate Core | Yes | No platform lock-in |
| Content | Content/Affiliate | Yes | Platform adaptations separate |
| AI generation | Content/AI | Yes | Provider adapter only |
| Media/video | Media | Yes | Distribution-specific transforms separate |
| Commission | Affiliate Core | Yes | Commerce provider adapter |
| Conversion | Affiliate Core | Yes | Source attribution metadata |
| Affiliate analytics | Affiliate Core | Yes | Distribution correlation allowed |
| Product sync | Commerce | Yes | Provider adapter |
| TikTok OAuth | TikTok Integration | No | TikTok only |
| TikTok account | TikTok Integration | No | TikTok only |
| TikTok upload | TikTok Integration | No | TikTok only |
| TikTok Direct Post | TikTok Integration | No | TikTok only |
| TikTok publishing status | TikTok Integration | No | TikTok only |
| TikTok metrics | Distribution Analytics | Yes | TikTok-specific metrics |
| Generic publishing | Distribution | Yes | Provider adapter |

## 3. Dependency rules

Allowed:

```text
Commerce Adapter → Ingestion → Affiliate Core
Affiliate Core → Content/Media
Affiliate Core → Publishing Port
Publishing Port → TikTok Adapter
TikTok Adapter → TikTok API
```

Forbidden:

```text
Affiliate Product → TikTok HTTP Client
Affiliate Campaign → TikTok OAuth
Affiliate Analytics → TikTok credentials
TikTok Adapter → direct mutation of canonical Product without an application contract
TikTok outage → Affiliate Core shutdown
```

## 4. Account model

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

## 5. Failure isolation

### TikTok unavailable

Affiliate products, offers, links, campaigns, content, media and analytics remain operational. Only affected distribution jobs may become `RETRYING` or `FAILED`.

### Commerce source unavailable

Existing canonical products remain usable. New synchronization is retried or marked failed; absence from one response must not imply deletion.

### AI provider unavailable

Existing content/media remain usable. New generation is queued/retried or fails explicitly.

### Media renderer unavailable

Source content and campaign state remain intact. Rendering jobs become retryable/failed.

## 6. External identity rules

Internal IDs are authoritative for authorization and relationships.

External IDs are references only:

```text
internalProductId != providerProductId
internalAccountId != tiktokOpenId
internalCampaignId != platformCampaignId
```

Never authorize a tenant using only an external provider ID.

## 7. Security ownership

Secrets belong only to the integration that requires them.

TikTok Client Secret, access tokens, refresh tokens and OAuth authorization codes must remain inside the TikTok integration boundary and secret store.

Commerce API credentials must remain inside their respective commerce provider boundary.

AI provider keys must remain inside the AI provider boundary.

Never expose integration secrets to browser code, generic Affiliate APIs, analytics events or logs.

## 8. Extension test

Before accepting a new integration, verify that adding it does not require changing Affiliate Core business rules.

A new commerce provider should require a provider adapter plus mapping/tests.

A new distribution provider should require a publishing adapter plus provider-specific tests.

If adding a provider requires widespread Affiliate changes, stop and correct the boundary before continuing.

# zTTato Security Policy

Report vulnerabilities privately via the repository's GitHub Security Advisory / private vulnerability channel where available, or reach the maintainer through a private agreed channel. Never disclose user media, personal data, access tokens, refresh tokens, Client Secrets, signed upload URLs, or vulnerability details in public issues.

## Boundaries
- Use official TikTok OAuth and Content Posting API only; never automate passwords, cookie extraction or unofficial browser uploads.
- Store TikTok tokens encrypted at rest on the backend, retain the encryption key outside source, validate one-use OAuth state and CSRF, protect session cookies, and require explicit consent before Direct Post.
- Validate any external upload URL against approved TikTok upload hostnames; bound media size, content type and storage access.
- Keep CI, CodeQL, Dependabot, dependency review and required PR reviews enabled when supported by repository plan. Never bypass a failing check.

## Incident actions
If a previous TikTok Developer Portal screenshot exposed the Client Secret, rotate it before enabling production, verify repository and log history contain no copies, and invalidate affected credentials. Rotate database encryption keys only with a documented token re-encryption or forced reconnect process.

## Supported versions
No production version has been certified. Availability targets, ownership, alerting, retention and recovery evidence must be documented before launch.

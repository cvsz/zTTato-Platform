# Operations

## Runtime
Run behind an HTTPS reverse proxy/Cloudflare tunnel. The app listens on loopback in Compose by default. Never expose PostgreSQL publicly.

## Secrets
Store TIKTOK_CLIENT_SECRET, APP_ENCRYPTION_KEY and POSTGRES_PASSWORD outside Git. Rotate credentials immediately if exposed in screenshots or logs. Token values and TikTok upload URLs must never be logged.

## Backup
Back up PostgreSQL with a consistent pg_dump and back up the token encryption key in a separate protected secret store. Media is operational/transient data and must follow an explicit retention policy.

## Restore
Restore into an isolated environment first, start the exact known-good image, verify /health/ready, decrypt a controlled test token record if applicable, and prove that production data was not overwritten. Capture timestamped evidence.

## Rollback
Keep immutable image digests/releases. Roll back application image first when schema-compatible. Database rollback requires a tested migration plan; never reverse a destructive migration by assumption.

## Incident priorities
1. Stop unauthorized publishing and revoke exposed credentials.
2. Preserve logs/evidence without recording secret values.
3. Isolate affected sessions/tokens.
4. Restore known-good runtime/data.
5. Verify TikTok authorization and publishing status before retrying jobs.

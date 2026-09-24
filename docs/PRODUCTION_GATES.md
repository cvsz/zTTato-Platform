# Production Readiness Gates

Production-ready is an evidence claim, not a branch name.

## P0 before production
- [ ] Main branch ruleset/protection requires review and green CI/security checks.
- [ ] Any TikTok Client Secret visible in screenshots, logs, chat or commits has been rotated.
- [ ] Production environment validation passes with HTTPS, PostgreSQL and persistent encryption key.
- [ ] Cloudflare/edge route exposes /, /privacy-policy, /terms-of-service and /tiktok/callback as required while admin surfaces remain protected.
- [ ] Exact TikTok redirect/domain/URL verification is complete.
- [ ] Legal entity, contact and postal address are real and counsel has reviewed public policies.
- [ ] Real Sandbox E2E evidence covers every requested product and scope.
- [ ] PostgreSQL backup plus isolated restore is executed and timestamped.
- [ ] Media retention/deletion behavior is verified.
- [ ] Known-good container/image rollback is executed and timestamped.
- [ ] Token encryption key backup/rotation and incident procedure is tested.
- [ ] Monitoring/alerts cover 5xx, OAuth failures, TikTok upstream errors, disk/media capacity and DB health.
- [ ] Rate-limit behavior and duplicate-post reconciliation are exercised.
- [ ] No credentials are present in repository history or artifacts.

## P1
- [ ] Schema migrations replace automatic create_all for production changes.
- [ ] Scheduled cleanup removes expired browser/OAuth records and expired media.
- [ ] Content Posting webhooks are validated and authenticated where adopted.
- [ ] SBOM, container vulnerability scan and provenance evidence are produced for releases.
- [ ] Load/soak baseline is documented.

Do not close these gates from documentation alone.

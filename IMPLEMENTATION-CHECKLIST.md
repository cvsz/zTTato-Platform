# zTTato Implementation Checklist

- [x] Import adaptable governance/security conventions from cvsz/ztemplate.
- [x] Use official TikTok OAuth and Content Posting APIs instead of password/browser automation.
- [x] Keep client secret and user tokens server-side.
- [x] Validate OAuth state and use secure cookies under HTTPS.
- [x] Encrypt stored TikTok tokens.
- [x] Require explicit creator consent for transfers.
- [x] Query current creator info before Direct Post and validate visibility/options.
- [x] Use idempotency records and reconciliation state around publish initiation.
- [x] Restrict TikTok upload destination to open-upload.tiktokapis.com.
- [x] Provide public Privacy Policy, Terms and review walkthrough.
- [x] Add Docker, Compose, unit tests, linting and container health CI.
- [x] Initial Alembic migration added; production create_all disabled. Real PostgreSQL upgrade, isolated restore and rollback evidence remain open.
- [ ] Configure main branch ruleset, required checks and review.
- [ ] Rotate potentially exposed TikTok secret and verify secret scanning.
- [ ] Verify production HTTPS/Cloudflare behavior from an external client.
- [ ] Execute real TikTok Sandbox end-to-end evidence.
- [ ] Execute backup/isolated restore and rollback evidence.
- [ ] Complete legal review and operator placeholders.

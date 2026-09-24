# zTTato Creator Platform

First-party TikTok creator application for https://zttato.zeaz.dev using official Login Kit and Content Posting API. Includes server-side encrypted tokens, draft uploads, consent-based direct posting, creator-info and publishing-status checks, legal pages, tests, Docker Compose and operations runbooks.

STATUS: implementation baseline; not TikTok-approved or verified production-ready. Run CI, real TikTok Sandbox review, legal signoff, isolated restore and deployment checks before launch.

STACK: Python 3.12+, FastAPI, SQLAlchemy, PostgreSQL 17, HTTPX, server-rendered legal pages, vanilla JS UI.

LOCAL SETUP:
1. Copy .env.example to .env. Generate APP_ENCRYPTION_KEY using: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
2. Enter your own real TikTok Client Key/Secret and legal entity, contact and address; never commit .env.
3. For local use: pip install -r requirements-dev.txt && uvicorn app.main:app --reload
4. For PostgreSQL: docker compose up --build -d
5. App: / ; review walkthrough: /review-preview ; legal: /privacy-policy and /terms-of-service.

Register https://zttato.zeaz.dev/tiktok/callback as the exact Web Login Kit redirect URI, if not already present. Never silently change registered redirects.
Review docs/TIKTOK_REVIEW.md, docs/OPERATIONS.md and docs/PRODUCTION_GATES.md.
Share Kit is NOT included: this web app uses Login Kit and Content Posting API only. No scraping or password automation is used.

CREATOR DASHBOARD: /dashboard provides real browser interactions for local MP4 upload, current TikTok visibility choices, commercial disclosure, consent, draft/direct requests, status polling and account controls. This page is not a substitute for real TikTok Sandbox E2E evidence.

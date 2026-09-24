# Schema migration runbook

Versioned schema migration is required for production. Database initialization by SQLAlchemy `create_all()` is **disabled** when `APP_ENV=production`.

## Fresh installation
1. Make an off-host PostgreSQL backup and preserve the encryption key separately.
2. Configure a URL-safe POSTGRES_PASSWORD (for example `openssl rand -hex 32`) and valid production .env.
3. Run `docker compose run --rm migrate`. This executes `alembic upgrade head`.
4. Run `docker compose up --build -d` and verify `/health/ready` externally over HTTPS.
5. Capture schema revision, timestamp and deployed image digest. The application checks that the production database revision matches code.

## Existing pre-Alembic installation
**Do not run the initial migration directly against an existing nonempty schema.** First take and test a restorable backup; compare the live schema to the initial revision using a temporary isolated database, have the operator approve any differences, and only after confirmed structural equivalence execute `alembic stamp 20260924_01`. Otherwise write an explicit repair migration.

## Rollback
Schema downgrades are for isolated rehearsal only. Before production rollback, confirm old application schema compatibility, preserve a verified database backup, and use an operator-approved migration path. Never automatically downgrade a live database.

## CI
`python -m pytest tests/test_migrations.py` verifies fresh upgrade and downgrade on an isolated temporary SQLite database. PostgreSQL migration/restore must be independently rehearsed before the production gate is satisfied.

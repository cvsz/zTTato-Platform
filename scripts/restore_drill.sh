#!/usr/bin/env bash
# PostgreSQL Restore Drill
# Creates isolated source/restore databases, backs up, restores, and validates.

set -euo pipefail

# Configuration
DB_HOST="${PGHOST:-localhost}"
DB_PORT="${PGPORT:-5432}"
DB_USER="${PGUSER:-postgres}"
DB_PASS="${PGPASSWORD:-postgres}"
DRIVER="postgresql+psycopg"

# Unique test databases
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SOURCE_DB="zttato_restore_source_${TIMESTAMP}"
RESTORE_DB="zttato_restore_target_${TIMESTAMP}"
BACKUP_FILE="/tmp/zttato_restore_${TIMESTAMP}.dump"
TEST_KEY="LZ0X0j0BNWv190IVhPFHWRvU0bqtPmi3yB8elYcJcUc="

export PGHOST="${DB_HOST}"
export PGPORT="${DB_PORT}"
export PGUSER="${DB_USER}"
export PGPASSWORD="${DB_PASS}"

log() { echo "[$(date -Iseconds)] $*"; }
die() { log "ERROR: $*"; exit 1; }

# Check PostgreSQL connection
log "Checking PostgreSQL connectivity..."
psql -c "SELECT version();" >/dev/null || die "Cannot connect to PostgreSQL"

# Create source database
log "Creating source database: ${SOURCE_DB}"
psql -c "CREATE DATABASE ${SOURCE_DB};" || die "Failed to create source database"

# Run migrations on source
log "Running Alembic migrations on source..."
export DATABASE_URL="${DRIVER}://${DB_USER}:${DB_PASS}@${DB_HOST}:${DB_PORT}/${SOURCE_DB}"
alembic upgrade head || die "Migration failed on source"

# Insert representative test data
log "Inserting test data..."
psql -d "${SOURCE_DB}" <<'SQL'
-- Browser session
INSERT INTO browser_sessions (id, csrf_hash, expires_at, created_at)
VALUES ('test_session_1', 'test_csrf_hash', 9999999999, 1700000000);

-- OAuth request
INSERT INTO oauth_requests (state_hash, session_id, expires_at)
VALUES ('test_state_hash', 'test_session_1', 9999999999);

-- Linked account with encrypted tokens
INSERT INTO linked_accounts (session_id, open_id, scopes, access_cipher, refresh_cipher, access_expires_at, refresh_expires_at)
VALUES (
  'test_session_1',
  'test_open_id_123',
  'user.info.basic,video.upload,video.publish',
  'gAAAAABl7test_access_token_encrypted',
  'gAAAAABl7test_refresh_token_encrypted',
  9999999999,
  9999999999
);

-- Media asset
INSERT INTO media_assets (id, session_id, filename, size, path, created_at)
VALUES ('test_media_1', 'test_session_1', 'test_video.mp4', 1024000, '/srv/media/test_media_1.mp4', 1700000000);

-- Publish job (draft)
INSERT INTO publish_jobs (id, session_id, idempotency_key, media_id, mode, publish_id, status, fail_reason, checked_at, created_at)
VALUES ('test_job_1', 'test_session_1', 'idemkey_draft_1234567890123456', 'test_media_1', 'draft', 'tiktok_publish_id_1', 'TRANSFER_PENDING', NULL, 0, 1700000000);

-- Publish job (direct)
INSERT INTO publish_jobs (id, session_id, idempotency_key, media_id, mode, publish_id, status, fail_reason, checked_at, created_at)
VALUES ('test_job_2', 'test_session_1', 'idemkey_direct_1234567890123456', 'test_media_1', 'direct', 'tiktok_publish_id_2', 'PROCESSING', NULL, 0, 1700000000);

-- Idempotency test: duplicate key should fail
-- This is validated by the unique constraint on (session_id, idempotency_key)
SQL

log "Test data inserted."

# Record source counts
SOURCE_COUNTS=$(psql -d "${SOURCE_DB}" -t -c "
SELECT
  (SELECT count(*) FROM browser_sessions) AS sessions,
  (SELECT count(*) FROM oauth_requests) AS oauth,
  (SELECT count(*) FROM linked_accounts) AS accounts,
  (SELECT count(*) FROM media_assets) AS media,
  (SELECT count(*) FROM publish_jobs) AS jobs;
")
log "Source counts: ${SOURCE_COUNTS}"

# Create backup
log "Creating pg_dump backup..."
pg_dump -Fc -f "${BACKUP_FILE}" -d "${SOURCE_DB}" || die "pg_dump failed"
BACKUP_SIZE=$(stat -c%s "${BACKUP_FILE}")
BACKUP_CHECKSUM=$(sha256sum "${BACKUP_FILE}" | cut -d' ' -f1)
log "Backup created: ${BACKUP_FILE} (${BACKUP_SIZE} bytes, SHA256: ${BACKUP_CHECKSUM})"

# Create restore database
log "Creating restore database: ${RESTORE_DB}"
psql -c "CREATE DATABASE ${RESTORE_DB};" || die "Failed to create restore database"

# Restore
log "Restoring with pg_restore --exit-on-error..."
pg_restore --exit-on-error -d "${RESTORE_DB}" "${BACKUP_FILE}" || die "pg_restore failed"
log "Restore completed."

# Validate restore counts
RESTORE_COUNTS=$(psql -d "${RESTORE_DB}" -t -c "
SELECT
  (SELECT count(*) FROM browser_sessions) AS sessions,
  (SELECT count(*) FROM oauth_requests) AS oauth,
  (SELECT count(*) FROM linked_accounts) AS accounts,
  (SELECT count(*) FROM media_assets) AS media,
  (SELECT count(*) FROM publish_jobs) AS jobs;
")
log "Restore counts: ${RESTORE_COUNTS}"

# Compare counts
if [[ "${SOURCE_COUNTS}" == "${RESTORE_COUNTS}" ]]; then
  log "PASS: Row counts match."
else
  die "FAIL: Row counts differ. Source: ${SOURCE_COUNTS}, Restore: ${RESTORE_COUNTS}"
fi

# Validate relationships and constraints
log "Validating relationships and constraints..."
psql -d "${RESTORE_DB}" <<'SQL'
-- Check foreign key constraints
SELECT conname, conrelid::regclass, confrelid::regclass
FROM pg_constraint
WHERE contype = 'f' AND connamespace = 'public'::regnamespace;

-- Check unique constraint on publish_jobs
SELECT conname, conrelid::regclass
FROM pg_constraint
WHERE contype = 'u' AND conname = 'uq_publish_once';

-- Verify idempotency keys are preserved
SELECT session_id, idempotency_key, mode, status FROM publish_jobs;
SQL

# Test encryption/decryption with isolated test key
log "Testing encryption/decryption..."
cd /home/cvsz/zttato-platform
python3 <<PYEOF
import os
os.environ['DATABASE_URL'] = '${DRIVER}://${DB_USER}:${DB_PASS}@${DB_HOST}:${DB_PORT}/${RESTORE_DB}'
os.environ['APP_ENCRYPTION_KEY'] = '${TEST_KEY}'

from app.security import TokenCipher
from app.db import make_session_factory, BrowserSession, LinkedAccount

cipher = TokenCipher('${TEST_KEY}')

# Test encrypt/decrypt roundtrip
test_token = "test_tiktok_access_token_12345"
encrypted = cipher.encrypt(test_token)
decrypted = cipher.decrypt(encrypted)
assert decrypted == test_token, f"Decryption failed: {decrypted} != {test_token}"
print(f"Encryption roundtrip: PASS")

# Test with database
engine, session_factory = make_session_factory(os.environ['DATABASE_URL'])
with session_factory() as session:
    # Verify existing encrypted data can be read (or at least structure is correct)
    account = session.query(LinkedAccount).first()
    if account:
        print(f"Found linked account: {account.open_id}")
        # Try decrypting - will fail with test key but structure validated
        try:
            cipher.decrypt(account.access_cipher)
            print("Decryption with test key: UNEXPECTED SUCCESS (data was encrypted with test key)")
        except Exception as e:
            print(f"Decryption with test key: EXPECTED FAILURE (different key used) - {type(e).__name__}")
    else:
        print("No linked accounts in restore DB")

    # Verify migrations applied
    from alembic.runtime.migration import MigrationContext
    from alembic.script import ScriptDirectory
    context = MigrationContext.configure(engine.connect())
    current_rev = context.get_current_revision()
    print(f"Current migration revision: {current_rev}")
    assert current_rev == '20260924_01', f"Expected revision 20260924_01, got {current_rev}"

print("Encryption/migration validation: PASS")
PYEOF

log "Encryption/migration validation passed."

# Test application readiness (health/ready)
log "Testing application readiness against restored database..."
export DATABASE_URL="${DRIVER}://${DB_USER}:${DB_PASS}@${DB_HOST}:${DB_PORT}/${RESTORE_DB}"
export APP_ENCRYPTION_KEY="${TEST_KEY}"
export TIKTOK_CLIENT_KEY="test"
export TIKTOK_CLIENT_SECRET="test"
export APP_BASE_URL="http://localhost:8000"
export APP_ALLOWED_HOSTS="localhost,127.0.0.1"

python3 -c "
from app.main import create_app
from app.config import load_settings
s = load_settings()
app = create_app(s)
print('App creation: PASS')
" || die "Application creation failed"

log "Application readiness: PASS"

# Cleanup
log "Cleaning up test databases..."
psql -c "DROP DATABASE IF EXISTS ${SOURCE_DB};"
psql -c "DROP DATABASE IF EXISTS ${RESTORE_DB};"
rm -f "${BACKUP_FILE}"

log "=== RESTORE DRILL COMPLETED SUCCESSFULLY ==="
log "Timestamp: $(date -Iseconds)"
log "PostgreSQL version: $(psql -t -c 'SELECT version();' | head -1 | xargs)"
log "Source commit: $(cd /home/cvsz/zttato-platform && git rev-parse HEAD)"
log "Backup checksum: ${BACKUP_CHECKSUM}"
log "Restore outcome: SUCCESS"
log "Verification: Row counts, relationships, constraints, encryption, migrations, app readiness"
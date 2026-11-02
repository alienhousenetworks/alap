#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
ENV_FILE="$ROOT/.env.prod"
[[ -f "$ENV_FILE" ]] || { echo "Missing infra/.env.prod" >&2; exit 1; }
set -a
source "$ENV_FILE"
set +a
: "${BACKUP_AGE_IDENTITY:?Set BACKUP_AGE_IDENTITY to a protected age identity file}"
: "${BACKUP_FILE:?Set BACKUP_FILE to an encrypted .dump.age backup}"
[[ -f "$BACKUP_FILE" ]] || { echo "Backup file not found" >&2; exit 1; }
command -v age >/dev/null || { echo "Install age before restore verification" >&2; exit 1; }
RESTORE_DB="alap_restore_check_$(date -u +%s)"
cleanup() {
  docker compose --env-file "$ENV_FILE" -f docker-compose.prod.yml exec -T postgres dropdb --if-exists -U "$POSTGRES_USER" "$RESTORE_DB" >/dev/null 2>&1 || true
}
trap cleanup EXIT
docker compose --env-file "$ENV_FILE" -f docker-compose.prod.yml exec -T postgres createdb -U "$POSTGRES_USER" "$RESTORE_DB"
age -d -i "$BACKUP_AGE_IDENTITY" "$BACKUP_FILE" \
  | docker compose --env-file "$ENV_FILE" -f docker-compose.prod.yml exec -T postgres pg_restore --exit-on-error --no-owner -U "$POSTGRES_USER" -d "$RESTORE_DB"
docker compose --env-file "$ENV_FILE" -f docker-compose.prod.yml exec -T postgres psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$RESTORE_DB" -c 'SELECT version_num FROM alembic_version;'
echo "Restore verification completed in temporary database $RESTORE_DB"

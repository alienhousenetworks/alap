#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
ENV_FILE="$ROOT/.env.prod"
[[ -f "$ENV_FILE" ]] || { echo "Missing infra/.env.prod" >&2; exit 1; }
set -a
source "$ENV_FILE"
set +a
: "${BACKUP_AGE_RECIPIENT:?Set BACKUP_AGE_RECIPIENT in infra/.env.prod}"
: "${BACKUP_DIR:=/var/backups/alap}"
command -v age >/dev/null || { echo "Install age before running encrypted backups" >&2; exit 1; }
mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
TMP="$BACKUP_DIR/alap-$STAMP.dump.age.tmp"
DEST="$BACKUP_DIR/alap-$STAMP.dump.age"
trap 'rm -f "$TMP"' EXIT
docker compose --env-file "$ENV_FILE" -f docker-compose.prod.yml exec -T postgres sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' \
  | age -r "$BACKUP_AGE_RECIPIENT" -o "$TMP"
test -s "$TMP"
mv "$TMP" "$DEST"
chmod 600 "$DEST"
find "$BACKUP_DIR" -type f -name 'alap-*.dump.age' -mtime +30 -delete
echo "Encrypted database backup created: $DEST"

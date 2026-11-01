#!/usr/bin/env bash
# Encrypted PostgreSQL backup; configure age and an off-host rclone remote first.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
AGE_RECIPIENT="${AGE_RECIPIENT:-$(sed -n 's/^AGE_RECIPIENT=//p' "$ROOT/.env.prod")}"
BACKUP_REMOTE="${BACKUP_REMOTE:-$(sed -n 's/^BACKUP_REMOTE=//p' "$ROOT/.env.prod")}"
: "${AGE_RECIPIENT:?Set AGE_RECIPIENT to the age public recipient in infra/.env.prod}"
: "${BACKUP_REMOTE:?Set BACKUP_REMOTE to an off-host rclone destination in infra/.env.prod}"
command -v age >/dev/null
command -v rclone >/dev/null
OUT="${1:-$ROOT/backups}"
mkdir -p "$OUT"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
PLAIN="$OUT/alap-$STAMP.dump"
ENCRYPTED="$PLAIN.age"
docker compose --env-file "$ROOT/.env.prod" -f "$ROOT/docker-compose.prod.yml" exec -T postgres pg_dump -U alap -d alap --format=custom --no-owner > "$PLAIN"
test -s "$PLAIN"
age -r "$AGE_RECIPIENT" -o "$ENCRYPTED" "$PLAIN"
shred -u "$PLAIN" 2>/dev/null || rm -f "$PLAIN"
rclone copyto "$ENCRYPTED" "$BACKUP_REMOTE/$(basename "$ENCRYPTED")"
echo "Encrypted backup uploaded to $BACKUP_REMOTE/$(basename "$ENCRYPTED")"

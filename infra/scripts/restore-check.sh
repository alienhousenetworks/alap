#!/usr/bin/env bash
# Restore into a throwaway database and verify the immutable credit-independent account schema.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INPUT="${1:?usage: restore-check.sh path/to/alap-*.dump[.age]}"
DUMP="$INPUT"
RESTORE_DB="alap_restore_check_$(date -u +%s)_${BASHPID}"
C=(docker compose --env-file "$ROOT/.env.prod" -f "$ROOT/docker-compose.prod.yml" exec -T postgres)
if [[ "$INPUT" == *.age ]]; then
  : "${AGE_IDENTITY:?Set AGE_IDENTITY to the protected private age identity file}"
  DUMP="$(mktemp)"
  age -d -i "$AGE_IDENTITY" -o "$DUMP" "$INPUT"
fi
cleanup() {
  "${C[@]}" psql -U alap -d postgres -c "DROP DATABASE IF EXISTS $RESTORE_DB" >/dev/null 2>&1 || true
  [[ "$DUMP" == "$INPUT" ]] || rm -f "$DUMP"
}
trap cleanup EXIT
"${C[@]}" psql -U alap -d postgres -v ON_ERROR_STOP=1 -c "CREATE DATABASE $RESTORE_DB"
"${C[@]}" pg_restore -U alap -d "$RESTORE_DB" --no-owner < "$DUMP"
"${C[@]}" psql -U alap -d "$RESTORE_DB" -v ON_ERROR_STOP=1 -c "SELECT count(*) FROM users"
echo "Restore smoke check succeeded; complete application-level verification is still required."

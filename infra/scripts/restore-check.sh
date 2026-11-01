#!/usr/bin/env bash
# Restore into a throwaway database and verify the immutable credit-independent account schema.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INPUT="${1:?usage: restore-check.sh path/to/alap-*.dump[.age]}"
DUMP="$INPUT"
if [[ "$INPUT" == *.age ]]; then
  : "${AGE_IDENTITY:?Set AGE_IDENTITY to the protected private age identity file}"
  DUMP="$(mktemp)"
  age -d -i "$AGE_IDENTITY" -o "$DUMP" "$INPUT"
fi
cleanup() { [[ "$DUMP" == "$INPUT" ]] || rm -f "$DUMP"; }
trap cleanup EXIT
C=(docker compose --env-file "$ROOT/.env.prod" -f "$ROOT/docker-compose.prod.yml" exec -T postgres)
"${C[@]}" psql -U alap -d postgres -v ON_ERROR_STOP=1 -c "DROP DATABASE IF EXISTS alap_restore_check" -c "CREATE DATABASE alap_restore_check"
"${C[@]}" pg_restore -U alap -d alap_restore_check --no-owner < "$DUMP"
"${C[@]}" psql -U alap -d alap_restore_check -v ON_ERROR_STOP=1 -c "SELECT count(*) FROM users"
"${C[@]}" psql -U alap -d postgres -c "DROP DATABASE alap_restore_check"
echo "Restore smoke check succeeded; complete application-level verification is still required."

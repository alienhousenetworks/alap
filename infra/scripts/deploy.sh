#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
test -f .env.prod || { echo "infra/.env.prod is required" >&2; exit 1; }
docker compose --env-file .env.prod -f docker-compose.prod.yml config -q
docker compose --env-file .env.prod -f docker-compose.prod.yml up --build -d --remove-orphans
API_DOMAIN="$(grep '^API_DOMAIN=' .env.prod | cut -d= -f2-)"
for _ in $(seq 1 30); do
  if curl --fail --silent "https://$API_DOMAIN/health/ready"; then
    echo "ALAP API is healthy"
    exit 0
  fi
  sleep 10
done
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
echo "ALAP failed readiness checks" >&2
exit 1

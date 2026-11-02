# ALAP production deployment and operations

This runbook describes a single-host Docker Compose deployment behind Caddy. It is a production baseline, not a substitute for a managed database, independent security review, or tested disaster-recovery process.

## Required infrastructure

- Linux host with supported Docker Engine and Docker Compose v2.
- DNS A/AAAA records for the web, admin and API domains pointing to the host.
- Inbound TCP 80/443 and optional UDP 443; SSH restricted to operator IPs.
- Private S3-compatible object storage with public access blocked and encryption enabled.
- OpenAI moderation/media credentials and the selected chat provider credentials.
- A protected age recipient for backups and an offline age identity for restore tests.
- Secrets stored outside source control. Never commit `.env.prod`.

## First deployment

1. Copy `infra/.env.prod.example` to `infra/.env.prod`.
2. Generate unique URL-safe database and Redis passwords and a high-entropy JWT secret. Build DATABASE_URL and REDIS_URL using those exact values.
3. Generate a Fernet key using the command in the environment example. Keep it in a secrets manager and back it up separately; losing it makes encrypted memories unreadable.
4. Configure a private S3 bucket, credentials, region and endpoint. Deny public bucket access. Configure lifecycle policies and server-side encryption.
5. Set real domains, ACME email, HTTPS CORS origins, selected AI provider/model, moderation key, and daily media quotas.
6. Validate secrets and DNS before launch. Never use the example values.
7. Run:

```bash
cd infra
docker compose --env-file .env.prod -f docker-compose.prod.yml config
docker compose --env-file .env.prod -f docker-compose.prod.yml build
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
```

8. Verify `https://api.example.com/health/live`, `/health/ready`, web and admin over TLS. Run an authenticated smoke test for login, chat, memory opt-in, image generation, speech generation, signed media retrieval and account deletion using disposable accounts.
9. Confirm database migration head and inspect logs for startup errors. Do not enable public sign-up until abuse limits, email verification, privacy/terms and moderation operations are approved.

## Network and secrets

- Only Caddy publishes ports. PostgreSQL, Redis, API, web and admin are on the private Compose network.
- Keep the host firewall closed except SSH, HTTP and HTTPS.
- Use a cloud firewall/security group in addition to host firewall rules.
- Rotate database, Redis, provider and object-storage credentials on a schedule and after staff changes.
- Keep JWT and memory encryption keys in a secrets manager. The memory key is data-critical and must be recoverable from a separate protected backup.
- Restrict S3 IAM to the ALAP bucket and required object operations. Never grant public ACLs.
- Do not enable debug endpoints or API documentation in production.

## Backups and recovery

Install `age` on the host. Set `BACKUP_AGE_RECIPIENT` in `.env.prod`, then schedule `infra/scripts/backup.sh` daily. Copy encrypted backups to a second region/account with object lock or immutable retention. Database backups do not include S3 media objects or encryption keys; back up the media bucket and key material separately.

Perform a monthly restore drill:

```bash
BACKUP_AGE_IDENTITY=/secure/path/age-identity.txt BACKUP_FILE=/var/backups/alap/alap-YYYYMMDDTHHMMSSZ.dump.age infra/scripts/restore-check.sh
```

A successful archive listing is not a restore drill: this script restores into a temporary database and checks the Alembic version table. Record duration, row counts, missing objects and recovery-point age. Do not run restore tests against the production database.

## Release and rollback

- Deploy immutable reviewed commits; record commit SHA, migration head and image digests.
- Run CI, staging smoke tests and migration compatibility checks before production.
- Take an encrypted backup before schema-changing releases.
- Apply backward-compatible expand/migrate/contract changes. Do not combine destructive schema drops with the same release that removes application compatibility.
- Roll back application images first where safe; use a forward fix for migrations unless a tested rollback procedure exists.
- Keep a human approval gate for production deploys, provider/model changes, spend-limit changes and public character moderation policy.

## Monitoring and incident response

Before launch, connect centralized structured logs, error tracking, traces and metrics. Alert on elevated 5xx/429 rates, database pool saturation, Redis failures, provider latency/errors, moderation failures, queue backlog, media quota anomalies, storage failures, backup age and disk pressure. Logs must redact authorization headers, refresh tokens, prompts containing personal data, generated media URLs and secrets.

Maintain an on-call contact, severity definitions, incident log, provider outage playbook, credential rotation playbook and customer communication templates. Test restore and rollback procedures; a green container health check is not operational readiness.

## Launch gates still requiring evidence

- Email verification and password reset delivery and abuse tests.
- Billing, Apple/Google receipt verification, wallet ledger and refunds.
- Independent penetration test, dependency/container scanning and authorization/IDOR review.
- Real provider contract tests, cost limits, retry/failover and load tests.
- Backup restore and S3 object recovery drill.
- iOS and Android signed release builds, physical-device QA and store policy review.
- Legal review of privacy, terms, age assurance, AI disclosures, retention and content policy.

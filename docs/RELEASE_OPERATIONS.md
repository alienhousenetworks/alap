# ALAP release and production operations

## Production deployment prerequisites

1. A hardened Linux host or managed container platform, DNS for API/web/admin, TLS and a monitored domain owner.
2. Managed PostgreSQL 16 and Redis 7 are preferred. If bundled Compose services are used, configure persistent encrypted volumes, disk alerts and off-host backups.
3. Create `infra/.env.prod` from `infra/.env.prod.example`; use unique random secrets. Never commit this file or provider credentials.
4. Configure the selected AI generation provider, OpenAI moderation and image/voice generation, private S3-compatible object storage, and explicit media cost estimates/monthly cap.
5. Configure provider-side spend limits, bucket lifecycle/backup, SMTP and DNS. Restrict admin access through VPN/IP allowlist before launch.
6. Run migrations and staging smoke tests, restore a recent encrypted backup, verify TLS and rollback, then complete independent security/privacy review.

## Guarded GitHub deployment workflow

`.github/workflows/deploy-production.yml` deploys only from `main` and requires the operator to type `DEPLOY`. Configure a protected GitHub `production` environment:

- Secrets: `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_SSH_PRIVATE_KEY`, `DEPLOY_KNOWN_HOSTS`.
- Variable: `DEPLOY_PATH` (absolute path, e.g. `/opt/alap`).
- Host: Docker Engine/Compose, a pre-provisioned `infra/.env.prod`, persistent volumes, backup tools and restricted SSH.

The workflow syncs source while preserving host secrets/backups, validates Compose, builds and starts services, applies migrations and checks API readiness. It does not provision the host, create DNS/firewall rules, create secrets or replace rollback/on-call procedures.

## Encrypted backup and restore

Install `age` and `rclone`; configure `AGE_RECIPIENT` and `BACKUP_REMOTE` on the host. Run `bash infra/scripts/backup.sh` to create an encrypted logical PostgreSQL backup and copy it off-host. For restore drills, set `AGE_IDENTITY` to the protected private age identity and run `bash infra/scripts/restore-check.sh path/to/backup.dump.age`. Keep the private identity outside the application host. Perform and record regular restore drills.

## Signed mobile builds

`.github/workflows/mobile-release.yml` produces signed Android App Bundle and iOS IPA artifacts when signing assets are configured. Required GitHub variable: `API_BASE_URL` (HTTPS API origin). Android secrets: `ANDROID_KEYSTORE_BASE64`, `ANDROID_KEY_ALIAS`, `ANDROID_KEY_PASSWORD`, `ANDROID_STORE_PASSWORD`. iOS secrets: `IOS_CERTIFICATE_BASE64` (distribution P12), `IOS_CERTIFICATE_PASSWORD`, `IOS_PROVISIONING_PROFILE_BASE64`, `IOS_TEAM_ID`; variable: `IOS_BUNDLE_ID`.

The generated Android identifier is `com.alienhousenetworks.alap`; confirm it with your Play Console before creating signing assets. Confirm the iOS bundle identifier with App Store Connect. Store signing keys in protected GitHub environments, never in Git. This workflow builds artifacts but does not submit them to either store.

## Store submission gates

Complete real-device QA, crash reporting, accessibility/localization, age-rating and age-assurance review, UGC moderation/report/block checks, privacy labels and Google Play Data Safety disclosures, privacy manifest/SDK declarations, screenshots, support URL, legal terms/privacy URLs, subscription disclosures and purchase/refund/restore-purchase sandbox tests. Obtain legal review. Store approval cannot be automated or guaranteed.

## Operations

Monitor API readiness, latency, 5xx rate, DB connections, Redis, provider failures, media spend, storage and moderation. Alert on failed migrations, stale/failed backups, failed restore drills, budget exhaustion and abnormal generation activity. Maintain a tested rollback procedure and named on-call owner. Run dependency, secret, container, authorization and penetration testing before public launch and after material security changes.

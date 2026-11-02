# Production Readiness Register

Status values: NOT_STARTED, IN_PROGRESS, VERIFIED, BLOCKED. A row is VERIFIED only when repeatable evidence exists. CI checks are not substitutes for live provider, security or operational verification.

| Area | Current status | Required evidence / remaining work |
|---|---|---|
| Repository foundation | IN_PROGRESS | Architecture and modular monolith boundaries exist; full code review remains |
| Backend runtime | IN_PROGRESS | CI has run backend tests and migrations against PostgreSQL/Redis on earlier revisions; latest commits require a fresh green run |
| Database schema/migrations | IN_PROGRESS | Alembic revisions 0001-0007 cover identity, characters, conversations, RBAC, moderation audit, reports, opt-in memory, private media and spend quotas; verify full upgrade/downgrade/rollback on staging |
| Authentication | IN_PROGRESS | Argon2, JWT access/refresh rotation, logout, current-user, password-confirmed deletion; email verification, password reset, MFA and device/session management remain |
| Rate limiting | IN_PROGRESS | Redis IP limits for registration/login and IP+account limits for chat, character creation, conversation creation and reporting; distributed abuse tests and trusted-proxy review remain |
| Authorization | IN_PROGRESS | Owner-scoped character/conversation APIs and admin role checks; exhaustive IDOR tests and independent authorization review remain |
| Character safety | IN_PROGRESS | Manual publication review, re-review after edits, user reports, admin triage and moderation audit; appeals, automated creator screening and specialist safety review remain |
| AI provider adapters | IN_PROGRESS | OpenAI, Anthropic and Google Gemini generation adapters; OpenAI moderation is mandatory for all providers and fails closed; failover, spend budgets and live provider contract tests remain |
| Conversations | IN_PROGRESS | Persistent turns, Redis per-conversation lock, bounded context, input/profile/output moderation, stable cursor pagination and consent-controlled long-term memory context; encrypted memory-at-rest (Fernet) now requires a production key, with key rotation, streaming, idempotency, load and race tests remaining |
| Billing | NOT_STARTED | Store sandbox receipts, payment integration, signed webhook handling and replay/idempotency tests |
| Wallet ledger | NOT_STARTED | Immutable ledger, atomic debits/refunds, concurrency and reconciliation |
| Image/voice | IN_PROGRESS | OpenAI image/TTS endpoints, input and generated-image moderation, private object storage, five-minute signed URLs, daily per-user quotas and PostgreSQL-serialized estimated monthly spend cap exist; live provider/storage tests, lifecycle/retention, rights review and actual invoice reconciliation remain |
| Flutter app | IN_PROGRESS | Auth, discovery/create/chat, opt-in encrypted memory controls, image previews and voice playback are implemented in source. Latest Dart edits still require Flutter analyze/build and real-device QA; native signing, store compliance and submission remain |
| Public website | IN_PROGRESS | Responsive marketing landing page and metadata; complete product/help/legal pages, analytics, SEO and accessibility review remain |
| Admin console | IN_PROGRESS | HttpOnly-cookie login proxy, API-enforced admin role, moderation queue, user reports and audit history; MFA, user/account operations, billing and provider operations remain |
| Privacy & compliance | IN_PROGRESS | Authenticated JSON account export and password-confirmed deletion with relational cascades; email/consent records, retention, external-provider and backup deletion, legal review and independent age assurance remain |
| Observability | NOT_STARTED | Structured redacted logs, traces, metrics, alerts, incident response and audit retention |
| Deployment | IN_PROGRESS | Hardened production Compose topology, Caddy TLS, migration job, health checks, encrypted age/rclone backup/restore scripts and guarded GitHub SSH deployment workflow are authored; host/DNS/secrets/TLS issuance, restore drill, rollback and production smoke tests are unverified |
| Security review | NOT_STARTED | Threat model, dependency/secret/container scanning, penetration test and independent authorization review |
| Store release | IN_PROGRESS | Signed Android AAB/iOS IPA workflow is authored and requires store signing secrets/profiles. Store accounts, signed build verification, device QA, privacy disclosures, legal URLs, sandbox purchase tests and actual submissions/approval remain outstanding |

## Verification evidence

- Earlier CI revisions passed backend tests and public-web builds; one earlier Flutter analysis passed and an Android debug build was later added to CI.
- A backend CI revision passed migrations against PostgreSQL and Redis after adding the moderation audit model. Revisions 0005-0006 and later provider, reporting and configuration changes still need a fresh green run.
- No production deployment, real AI provider request, billing/store purchase test, signed App Store/Play Store archive, penetration test or backup-restore test has been performed.

This register is intentionally conservative. ALAP is not approved for production launch until all critical gates are verified.
\n\n- 2026-11-01: Branch `production/ai-memory-media-ops` adds migration 0007, consent-controlled memory APIs and mobile UI, OpenAI image/voice generation with private storage, moderation, daily quotas and a database-serialized monthly estimated budget, plus deployment/backup/mobile-signing workflows. These additions require fresh CI and live integration verification before production.\n
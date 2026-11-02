# Production Readiness Register

Status values: NOT_STARTED, IN_PROGRESS, VERIFIED, BLOCKED. A row is VERIFIED only when repeatable evidence exists. CI checks are not substitutes for live provider, security or operational verification.

| Area | Current status | Required evidence / remaining work |
|---|---|---|
| Repository foundation | IN_PROGRESS | Architecture and modular monolith boundaries exist; full code review remains |
| Backend runtime | IN_PROGRESS | Existing CI passed earlier revisions; this feature branch requires fresh migration, unit and integration test results |
| Database schema/migrations | IN_PROGRESS | Revisions 0001-0008 now include opt-in memory and media metadata; verify clean upgrade, downgrade and restore on staging |
| Authentication | IN_PROGRESS | Argon2, JWT access/refresh rotation, logout, current-user, password-confirmed deletion; email verification, password reset, MFA and device/session management remain |
| Rate limiting | IN_PROGRESS | Redis IP/account limits plus daily image and speech quotas; distributed abuse and spend-limit tests remain |
| Authorization | IN_PROGRESS | Owner-scoped APIs and approved public-character memory; exhaustive IDOR tests and independent authorization review remain |
| Character safety | IN_PROGRESS | Manual publication review, re-review after edits, user reports, admin triage and moderation audit; appeals and specialist safety review remain |
| AI provider adapters | IN_PROGRESS | OpenAI, Anthropic and Gemini chat generation; mandatory OpenAI moderation; failover, spend budgets and live provider contract tests remain |
| Conversations | IN_PROGRESS | Persistent turns, Redis conversation lock, bounded context, moderation and cursor pagination; streaming, idempotency, load and race tests remain |
| Long-term AI memory | IN_PROGRESS | Opt-in per-user/per-character memory, Fernet-encrypted content, HMAC deduplication, conservative extraction, memory injection and inspect/delete controls added; extraction quality, key rotation, privacy review and end-to-end tests remain |
| Image generation | IN_PROGRESS | OpenAI image generation, prompt/output moderation, private S3-compatible storage, signed retrieval and daily quotas added; real provider/storage tests, cost budgets and lifecycle tests remain |
| Voice generation | IN_PROGRESS | OpenAI text-to-speech, text moderation, private object storage, signed retrieval and mobile playback added; real provider/storage/device tests and spend controls remain |
| Wallet and billing | NOT_STARTED | Immutable ledger, Apple/Google receipt validation, signed webhooks, refunds, reconciliation and restore purchases |
| Flutter app | IN_PROGRESS | Auth, discovery, chat, memory controls, image and voice tools; signed release builds and physical-device QA remain |
| Public website | IN_PROGRESS | Landing page and metadata; full product/help/legal pages, accessibility and analytics review remain |
| Admin console | IN_PROGRESS | Moderation queue, user reports and audit history; MFA, account operations, billing and provider operations remain |
| Privacy & compliance | IN_PROGRESS | Account export/deletion and memory/media controls; legal review, retention, age assurance, consent and provider disclosures remain |
| Observability | NOT_STARTED | Centralized redacted logs, metrics, traces, alerts, incident response and audit retention |
| Production deployment | IN_PROGRESS | Private-network Compose/Caddy baseline, secret template, encrypted database backup and real temporary-database restore-check scripts added; staging/production deployment, managed services, S3 recovery, monitoring and restore drill remain |
| Security review | NOT_STARTED | Threat model, dependency/secret/container scanning, penetration test and independent authorization review |
| App Store / Play Store | IN_PROGRESS | Manual signed Android AAB and iOS IPA build workflow plus store checklist added; signing secrets, physical QA, privacy labels, store submission and approval remain |

## Evidence and honest status

- The main branch previously had a green backend/web/mobile CI run. That does not verify this branch's new code.
- No live image or voice generation, private S3 storage, production deployment, production backup restore, penetration test, signed store artifact, purchase test or store approval has been verified.
- The release workflow only builds signed artifacts when the required Apple/Google secrets and bundle identifiers are configured. It does not submit the app to either store.
- Production is not approved until the critical gates above have repeatable evidence and operational owners.

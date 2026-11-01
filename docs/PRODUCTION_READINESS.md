# Production Readiness Register

Status values: NOT_STARTED, IN_PROGRESS, VERIFIED, BLOCKED. A row is VERIFIED only when repeatable evidence exists. CI checks are not substitutes for live integration, security or operational verification.

| Area | Current status | Required evidence / remaining work |
|---|---|---|
| Repository foundation | IN_PROGRESS | Architecture and baseline files exist; complete code review remains |
| Backend runtime | IN_PROGRESS | CI installs API, Ruff correctness checks and pytest pass on a prior PR revision; rerun after latest commits |
| Database schema/migrations | IN_PROGRESS | Alembic migrations 0001-0003 exist; run upgrade/downgrade against real PostgreSQL and test rollback |
| Authentication | IN_PROGRESS | Registration, login, Argon2, JWT access/refresh rotation, logout, current-user and account deletion routes; email verification, password reset, MFA, session/device management and integration tests remain |
| Rate limiting | IN_PROGRESS | Redis-backed IP throttles on registration/login/chat; distributed abuse testing, per-account limits and proxy trust configuration remain |
| Authorization | IN_PROGRESS | Owner-scoped character/conversation access and admin role dependency; exhaustive IDOR tests and role administration review remain |
| Character platform | IN_PROGRESS | Owner CRUD/discovery, pending-review state, re-review after owner edits, admin queue, approve/reject, append-only moderation audit feed, user safety reports and admin report triage; appeals and richer safety review remain |
| AI provider adapters | IN_PROGRESS | OpenAI, Anthropic and Google Gemini generation adapters; OpenAI moderation is mandatory for every provider and fails closed; provider failover, budget enforcement and live contract tests remain |
| Conversations | IN_PROGRESS | Persistent conversations/messages; input and output moderation fail closed through OpenAI Moderation API; streaming, retries, idempotency, concurrency/load tests and memory lifecycle remain |
| Billing | NOT_STARTED | Store sandbox receipts, payment provider integration, webhook signature/replay/idempotency tests |
| Wallet ledger | NOT_STARTED | Immutable ledger, atomic debits/refunds, concurrency and reconciliation |
| Image/voice | NOT_STARTED | Provider adapters, moderation, storage lifecycle, rights controls and cost limits |
| Flutter app | IN_PROGRESS | Auth, secure token storage/refresh, character discovery/create, chat and account shell; native platform projects, device builds, accessibility and integration tests remain |
| Public website | IN_PROGRESS | Initial responsive landing page; full product, pricing, legal, SEO, analytics and accessibility review remain |
| Admin UI | IN_PROGRESS | Initial console shell; protected login, MFA, role-aware screens and API integration remain |
| Privacy & compliance | IN_PROGRESS | Authenticated JSON account export and password-confirmed account deletion with relational cascades; consent records, retention, deletion propagation to external providers/backups, policy/legal review and independent age assurance remain |
| Observability | NOT_STARTED | Structured redacted logs, traces, metrics, alerts, incident response and audit retention |
| Deployment | NOT_STARTED | Production secrets, TLS, managed DB/Redis, object storage, backups/restore, rollback, staging and production smoke tests |
| Security review | NOT_STARTED | Threat model, dependency/secret scanning, penetration test and independent authorization review |
| Store release | NOT_STARTED | iOS/Android release signing, privacy labels, store policy review and approved submissions |

## Current verification evidence

- GitHub Actions has reported backend and public-web jobs successful for commit `997979604efcf56c4731778029c5afee2ae440a0`.
- Flutter static analysis passed on that revision; the Android build failed because the repository did not yet contain native Android platform scaffolding. A subsequent workflow change generates native scaffolding in CI, and that change still requires a completed green run.
- Later backend changes add Redis throttling, PostgreSQL migration execution in CI, RBAC, moderation, moderation audit records and account export. The latest backend CI job passed against PostgreSQL and Redis services; live provider, deployment and security testing remain.
- No production deployment, real provider request, billing test, App Store/Play Store build, penetration test or data restore test has been performed.

This register is intentionally conservative. The application is not approved for production launch until all critical gates are verified.

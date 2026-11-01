# Production Readiness Register

Status values: NOT_STARTED, IN_PROGRESS, VERIFIED, BLOCKED. Do not mark VERIFIED without test evidence.

| Area | Current status | Required evidence |
|---|---|---|
| Repository foundation | IN_PROGRESS | Review all checked-in files |
| Backend runtime | IN_PROGRESS | Install, start, tests, type/lint |
| Database schema/migrations | NOT_STARTED | Alembic migrations + upgrade/downgrade tests |
| Authentication | NOT_STARTED | Registration/login/refresh/revocation tests |
| Authorization | NOT_STARTED | Cross-user access and role tests |
| Character CRUD/publishing | NOT_STARTED | API + moderation integration tests |
| AI provider adapters | NOT_STARTED | Live sandbox contract tests |
| Conversation streaming | NOT_STARTED | Persistence, retries, disconnect tests |
| Memory lifecycle | NOT_STARTED | Relevance, consent, delete propagation tests |
| Billing | NOT_STARTED | Store sandbox receipts and webhook replay tests |
| Wallet ledger | NOT_STARTED | Concurrency, idempotency and reconciliation tests |
| Image/voice | NOT_STARTED | Provider contracts, moderation and cost controls |
| Flutter app | IN_PROGRESS | Device builds, navigation, integration tests |
| Public website | IN_PROGRESS | SEO, accessibility, responsive and build checks |
| Admin | IN_PROGRESS | MFA, RBAC, audit and API integration |
| Observability | NOT_STARTED | Dashboards, alerts, tracing, redaction |
| Deployment | NOT_STARTED | TLS, secrets, backups, restore and rollback |
| Security review | NOT_STARTED | Threat model, dependency scan, penetration test |
| Store release | NOT_STARTED | Policy review and approved store submissions |

The initial repository commits are a foundation only. No production-readiness claim is permitted until each critical row is evidenced.

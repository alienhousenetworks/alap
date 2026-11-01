# ALAP Product & System Architecture

## Product
ALAP is an AI character universe. Users discover and create fictional AI characters, hold persistent conversations, participate in interactive stories, and optionally use generated images and voice. The system must clearly disclose that characters are AI.

## Applications
1. Flutter mobile app: onboarding, discovery, character creation, chat, memory controls, subscription, wallet, profile and safety.
2. Next.js public site: product landing pages, SEO metadata, pricing, help, legal pages and app-store links.
3. Next.js admin: users, characters, moderation, provider health, billing reconciliation, usage, analytics and audit logs.
4. FastAPI API: identity, character catalog, conversation orchestration, memory, billing, media jobs, moderation and admin APIs.

## Backend architecture
Start as a modular monolith with strict module boundaries. Extract services only when measured scaling or operational requirements justify it.

Modules:
- identity, users, devices, consent
- characters, categories, creator publishing
- conversations, messages, context assembly
- AI gateway, model registry, provider adapters
- memory extraction, retrieval, lifecycle and deletion
- relationship and story state
- media jobs, image and voice adapters
- products, subscriptions, receipts, wallet ledger
- moderation, reports, appeals
- notifications, analytics, admin and audit

## Runtime message flow
1. Authenticate user and authorize conversation ownership.
2. Load character version and safety policy.
3. Check server-side entitlement, quota and wallet.
4. Apply input moderation and abuse controls.
5. Assemble bounded context from character definition, recent turns and relevant user-approved memories.
6. Route to configured provider/model with timeout and bounded retries.
7. Moderate generated output.
8. Persist user/assistant messages and usage event transactionally.
9. Settle usage/credits idempotently; reconcile provider usage.
10. Update memory asynchronously and emit observability events.

## Data principles
- PostgreSQL is source of truth.
- pgvector stores embeddings linked to deletable source records.
- Redis is cache/queue support, never financial source of truth.
- Wallet uses immutable ledger entries; balance is derived or transactionally maintained.
- Subscription entitlement is server-authoritative and verified against store/provider events.
- Every user-owned row is scoped and authorized server-side.
- Conversation content is private by default.

## Production gates
No claim of production readiness until migrations, automated tests, provider integrations, store receipt validation, privacy deletion, moderation, observability, backup/restore, load tests, security review and deployment runbooks are verified.

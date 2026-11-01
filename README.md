# ALAP — AI Companion & Character Universe

ALAP is being developed as an AI character and interactive-story platform with Flutter mobile apps, a FastAPI API, a Next.js public marketing site and a separate operations console.

## Repository layout
- `apps/mobile` — Flutter iOS/Android application source
- `apps/web` — public Next.js marketing site
- `apps/admin` — Next.js operations console
- `services/api` — FastAPI modular monolith
- `infra` — local and production Docker Compose, Caddy, deployment and encrypted backup scripts
- `docs` — architecture, API, security, development and production-readiness documentation

## Current implementation status
The repository began empty and is still under active implementation. It now contains account authentication, character CRUD/discovery, persistent chat, AI provider adapters, safety moderation/reporting, admin moderation, account export/deletion, opt-in long-term memory, private image/voice generation and a Flutter client. Production deployment and signed mobile release workflows are authored, but still require credentials and live verification. It is **not yet a production release**.

Billing/wallet, email verification, password reset, independent age assurance, observability, live production deployment, provider spend reconciliation, store metadata, device QA and actual store submissions remain incomplete or unverified. See `docs/PRODUCTION_READINESS.md`, `docs/MEMORY_AND_MEDIA.md` and `docs/RELEASE_OPERATIONS.md` for evidence-based gates and operational setup.

## Local development
See `docs/DEVELOPMENT.md`. Never commit secrets. Use generated secrets locally and a managed secrets store in deployed environments.

## Core principles
- Server-authoritative identity, entitlements and billing.
- AI provider abstraction with explicit configuration.
- User-controlled memory and privacy lifecycle.
- Safety checks at user input, character profile and generated output boundaries.
- Auditable administrative decisions.
- No simulated provider success or fabricated usage metrics.

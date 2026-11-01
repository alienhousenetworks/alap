# ALAP — AI Companion & Character Universe

ALAP is being developed as an AI character and interactive-story platform with Flutter mobile apps, a FastAPI API, a Next.js public marketing site and a separate operations console.

## Repository layout
- `apps/mobile` — Flutter iOS/Android application source
- `apps/web` — public Next.js marketing site
- `apps/admin` — Next.js operations console
- `services/api` — FastAPI modular monolith
- `infra` — local Docker Compose development dependencies and API container
- `docs` — architecture, API, security, development and production-readiness documentation

## Current implementation status
The repository began empty and is still under active implementation. It now contains account authentication, character CRUD/discovery, persistent chat, AI provider adapters, safety moderation/reporting, admin moderation, account export/deletion and a Flutter client. It is **not yet a production release**.

Billing, wallet/credits, long-term memory, image/voice generation, email verification, password reset, age assurance, observability, production deployment and signed store releases remain incomplete or unverified. See `docs/PRODUCTION_READINESS.md` for the evidence-based gate list.

## Local development
See `docs/DEVELOPMENT.md`. Never commit secrets. Use generated secrets locally and a managed secrets store in deployed environments.

## Core principles
- Server-authoritative identity, entitlements and billing.
- AI provider abstraction with explicit configuration.
- User-controlled memory and privacy lifecycle.
- Safety checks at user input, character profile and generated output boundaries.
- Auditable administrative decisions.
- No simulated provider success or fabricated usage metrics.

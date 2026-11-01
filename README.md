# ALAP — AI Companion & Character Universe

A production-oriented AI companion platform: Flutter mobile apps, FastAPI backend, Next.js marketing site and admin console.

## Repository layout
- `apps/mobile` — Flutter iOS/Android application
- `apps/web` — Next.js landing site and authenticated web experience
- `apps/admin` — Next.js operations console
- `services/api` — FastAPI application
- `infra` — Docker, deployment and observability
- `docs` — architecture, security, operations and product specifications

## Development status
This repository is being built from an empty starting point. The checked-in foundation is not yet a production release. Production readiness requires completing the modules, configuring real provider credentials and store accounts, running migrations, tests, security review, load tests and deployment verification.

## Local development
See `docs/DEVELOPMENT.md`. Never commit secrets. Copy environment templates and use a secrets manager for deployed environments.

## Core principles
- Server-authoritative identity, entitlements, wallet and billing.
- AI provider abstraction; no provider lock-in.
- Explicit, user-controllable memory.
- Safety and age controls at every content boundary.
- Auditable financial ledger and administrative actions.
- No simulated provider success or fabricated analytics.

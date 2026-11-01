# Development Guide

## Prerequisites
- Python 3.12+
- Flutter stable channel and Dart SDK
- Node.js LTS and pnpm
- Docker + Docker Compose
- PostgreSQL with pgvector (or compose service)
- Redis

## Services
- API: `services/api`
- Mobile: `apps/mobile`
- Public web: `apps/web`
- Admin: `apps/admin`

## Environment
Copy each `.env.example` to a local ignored `.env`. Never commit real API keys, signing keys, database passwords, store credentials or JWT secrets.

## Quality gates
- Backend: Ruff, mypy, pytest and migration checks.
- Flutter: dart format, flutter analyze and flutter test.
- Web/admin: ESLint, TypeScript checks and production builds.
- Integration: PostgreSQL/Redis, billing webhook fixtures, provider contract tests.
- Security: dependency scan, secret scan, authorization tests and OWASP review.

A green local build does not prove production readiness. Provider credentials, store sandbox accounts, domain/DNS, TLS, backups and deployment environment must be independently configured and verified.

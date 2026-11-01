# Development Guide

## Prerequisites
- Python 3.12+
- Flutter stable channel and Dart SDK
- Node.js 22+
- Docker + Docker Compose
- Git

## Repository services
- API: `services/api`
- Mobile: `apps/mobile`
- Public website: `apps/web`
- Admin console: `apps/admin`

## Environment
Copy `services/api/.env.example` to `services/api/.env` and set a unique random `JWT_SECRET`. Configure database, Redis and provider values as needed. Never commit real API keys, signing keys, database passwords, store credentials or JWT secrets.

## Run the full local stack

From the repository root:

```bash
docker compose -f infra/docker-compose.yml up --build
```

The compose file starts PostgreSQL, Redis, the API, the public website and the admin console. The API runs Alembic migrations before starting and exposes readiness at `/health/ready`.

- Public website: http://localhost:3000
- Admin console: http://localhost:3001
- API: http://localhost:8000
- API docs (development only): http://localhost:8000/docs

To create an administrator, first register an account through the app/API, then run from the repository root:

```bash
docker compose -f infra/docker-compose.yml exec api python scripts/promote_admin.py your-account@example.com
```

This command changes the account role in the database. Run it only from a trusted operator shell.

## Run individual services

Backend:

```bash
cd services/api
python -m pip install -e '.[dev]'
alembic upgrade head
uvicorn app.main:app --reload
pytest
```

Web and admin:

```bash
npm install
npm run web:dev
npm run admin:dev
```

Flutter:

```bash
cd apps/mobile
flutter create --platforms=android,ios --org com.alap.app .
flutter pub get
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000
```

Use `http://127.0.0.1:8000` for iOS simulator and a reachable LAN HTTPS URL for physical devices. Release builds must use HTTPS.

## Quality gates
- Backend: Ruff, pytest, Alembic migrations against PostgreSQL and Redis.
- Flutter: `flutter analyze`, `flutter test` and Android build.
- Web/admin: TypeScript compilation and production Next.js builds.
- Integration: provider contract tests, billing sandbox tests and full API/mobile E2E tests.
- Security: dependency scan, secret scan, authorization tests, threat model and independent OWASP review.

A green CI build does not prove production readiness. Provider credentials, store sandbox accounts, domain/DNS, TLS, backups and deployment environment must be independently configured and verified. The included Compose file is for local development, not production hosting.

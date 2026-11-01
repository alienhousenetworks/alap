# API Reference (current implementation)

Base path: `/api/v1`. All endpoints except system and health require a bearer access token.

## System
- `GET /health/live` — process liveness.
- `GET /health/ready` — checks PostgreSQL and Redis.
- `GET /api/v1/system` — API identity/version.

## Authentication
- `POST /auth/register` — email, password (12+ characters), display_name, confirm_adult.
- `POST /auth/login` — email/password.
- `POST /auth/refresh` — refresh_token; rotates the refresh session.
- `POST /auth/logout` — refresh_token; revokes that refresh session.
- `GET /auth/me` — current account.
- `GET /auth/me/export` — export account profile, owned characters, conversations and messages as JSON.
- `DELETE /auth/me` — password-confirmed account deletion.

Access tokens are short-lived JWTs. Refresh-token identifiers are persisted and rotated. Passwords use Argon2. Email verification and password reset are not implemented yet; registration currently relies on user age confirmation and must not be treated as age assurance.

## Characters
- `GET /characters/discover` — approved, published public characters.
- `GET /characters/mine` — caller-owned characters.
- `POST /characters` — create a private, pending-moderation character.
- `GET /characters/{id}` — owner or approved-public access.
- `PATCH /characters/{id}` — owner update.
- `DELETE /characters/{id}` — owner deletion.

A user cannot publish a character directly. Public visibility requires administrator approval.

## Conversations
- `GET /conversations` — caller-owned conversations.
- `POST /conversations` — start a conversation with an owned or approved-public character.
- `GET /conversations/{id}/messages` — paginated message history.
- `POST /conversations/{id}/messages` — generate and persist a user/assistant turn using the configured AI provider.

The current chat route is synchronous and uses the most recent 20 messages. User input and generated output are checked through the OpenAI Moderation API; if moderation is unavailable, the turn fails closed and is not persisted. Streaming, durable long-term memory, and provider failover are not implemented yet.

## Administration
- `GET /admin/moderation/characters?status=pending` — admin moderation queue.
- `POST /admin/characters/{id}/approve` — approve; publishes only if visibility is public.
- `POST /admin/characters/{id}/reject` — reject with a reason.
- `GET /admin/audit/moderation` — read-only moderation decision history, newest first.

Bootstrap an administrator only from a trusted operator shell after creating the account:
`cd services/api && python scripts/promote_admin.py admin@example.com`

The admin UI is not yet wired to these APIs. Keep the bootstrap command restricted to authorized operators.

## Local setup
1. Copy `services/api/.env.example` to `services/api/.env`; set a unique random `JWT_SECRET`.
2. Run `docker compose -f infra/docker-compose.yml up --build`.
3. The API container runs `alembic upgrade head` before starting.
4. Configure `OPENAI_API_KEY`, `AI_DEFAULT_PROVIDER=openai`, and `AI_DEFAULT_MODEL` to enable chat.
5. For Flutter, use `--dart-define=API_BASE_URL=https://your-api-domain` (without the `/api/v1` suffix).

Never commit real secrets. The Compose defaults are for local development only, not production deployment.

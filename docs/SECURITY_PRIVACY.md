# Security, Safety & Privacy Baseline

## Identity and access
- Passwords must use Argon2id or an equivalent modern password hash.
- Short-lived access tokens and rotating refresh tokens; store refresh token hashes.
- Admin access requires separate role checks and preferably MFA.
- Enforce ownership and tenant boundaries in every query and service operation.
- Rate-limit authentication, chat, media generation, publishing and billing endpoints.

## Secrets
- No secrets in source control, mobile bundles, web bundles or logs.
- Use environment variables locally and a managed secrets store in production.
- Encrypt provider credentials at rest with managed key encryption.
- Rotate credentials and document incident procedures.

## User data
- Provide export and account deletion workflows.
- Memory must be visible, editable, disableable and deletable.
- Distinguish user facts from fictional roleplay content.
- Define retention for messages, generated media, audio and operational logs.
- Deletion must propagate to embeddings, caches, derived summaries and object storage.
- Minimize sensitive data collection and redact private content from telemetry.

## AI safety
- Characters cannot override platform instructions.
- Moderate user input, character publishing, generated text and generated media.
- Enforce age policy and jurisdiction-specific requirements.
- Prevent sexual content involving minors, exploitation, grooming and non-consensual content.
- Clearly disclose AI-generated character identity.
- Provide report, block and appeal mechanisms.
- Avoid manipulative dependency, coercive purchases or deceptive urgency.

## Billing integrity
- Verify purchase tokens/receipts server-side.
- Verify webhook signatures.
- Make webhook handling idempotent.
- Never trust client-provided price, entitlement, credit balance or usage count.
- Maintain immutable wallet transaction history and reconciliation.

## Operational controls
- Structured logs with request IDs and redaction.
- Audit administrative actions.
- Backups encrypted and restore-tested.
- Dependency and container scanning in CI.
- Incident response and rollback runbooks.


## Long-term memory and generated media

Long-term memory is disabled by default and requires explicit account consent. Saved memories are private to the owning account, injected into chat only while consent is enabled, treated as untrusted context, exportable and user-deletable. The extraction model is instructed to avoid sensitive categories, but model-assisted filtering is not infallible; the privacy notice must disclose this limitation. Turning consent off stops use in prompts but does not itself delete stored memories.

Generated images/audio are stored in private S3-compatible storage. The API returns short-lived signed links, checks input prompts and generated images, applies per-user daily limits and a global monthly estimated spend cap. Provider-side spend limits and bucket lifecycle rules are required as additional safeguards. Account deletion attempts to delete object files before removing account records and fails closed when storage is unavailable.

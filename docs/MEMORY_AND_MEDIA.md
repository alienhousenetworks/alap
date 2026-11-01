# ALAP long-term memory and generated media

## Long-term memory

Memory is disabled by default and is explicitly opt-in per account. The Flutter profile exposes the consent switch, saved-memory list, manual memory creation and deletion. The API supports:

- `GET /api/v1/memory/consent` and `PUT /api/v1/memory/consent`
- `GET /api/v1/memory`, `POST /api/v1/memory`
- `PATCH /api/v1/memory/{id}`, `DELETE /api/v1/memory/{id}`, `DELETE /api/v1/memory`
- `POST /api/v1/memory/extract/{conversation_id}` (requires consent and is rate limited)

Extraction runs periodically in the mobile chat flow only after consent is enabled. It reads only user-authored messages, asks the configured AI provider for up to five durable, non-sensitive facts, rejects malformed output, moderates each extracted fact, deduplicates exact matches and caps storage at 100 memories per account. The extraction prompt explicitly excludes sensitive personal data and credentials. This is model-assisted filtering, not a guarantee that sensitive facts can never be extracted; privacy disclosures must say so.

Memory is inserted into the character prompt as untrusted context, never as privileged system instructions. Turning memory off prevents all saved memories from being injected into chat but retains them for later re-enabling. Users can inspect, edit, disable or delete memories, including deleting all. Account export includes memory records; account deletion cascades memory records.

## Image and voice generation

- `POST /api/v1/media/images`: OpenAI image generation, bounded size/aspect ratio, input moderation and image-aware moderation of generated output.
- `POST /api/v1/media/voice`: OpenAI text-to-speech after text moderation using standard synthetic voices; this is not voice cloning or a custom character voice model.
- `GET /api/v1/media`: list the authenticated user's media with short-lived signed links.
- `DELETE /api/v1/media/{id}`: delete the private object and metadata.

Generated files are stored in a private S3-compatible bucket. PostgreSQL stores only metadata and private object keys. Download links expire after five minutes. The API enforces account/IP rate limits, per-user daily image/voice quotas, a global monthly estimated-spend cap, and a maximum media size. Monthly budget reservations are serialized in PostgreSQL so concurrent API instances cannot exceed the configured estimate. Failed provider/storage operations release the reservation where possible. Account deletion removes stored objects before deleting the account and fails closed if object storage is unavailable.

Set `IMAGE_GENERATION_MODEL`, `VOICE_GENERATION_MODEL`, `MEDIA_DAILY_IMAGE_LIMIT`, `MEDIA_DAILY_VOICE_CHARACTERS`, `MEDIA_MONTHLY_BUDGET_USD`, `MEDIA_IMAGE_ESTIMATED_COST_USD`, and `MEDIA_VOICE_ESTIMATED_COST_PER_1K_CHARS_USD` from the current provider pricing and your own spend tolerance. Cost estimates are operator-supplied safeguards, not live provider billing data. Reconcile them against provider invoices and set provider-side hard spend limits as a second control. Production refuses to start without positive estimates and a positive monthly cap.

Configure a private bucket with encryption at rest, lifecycle rules, restricted credentials and backup policy. Never enable public bucket access. Define deletion and retention periods for backups and provider-side data separately; do not promise instantaneous removal from immutable backups.

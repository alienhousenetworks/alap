import base64
from uuid import UUID, uuid4
from datetime import datetime, timezone
import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.ai.registry import build_provider
from app.api.deps import account_rate_limit, get_current_user, rate_limit
from app.core.config import settings
from app.db.session import get_db
from app.models.conversation import Conversation
from app.models.media_asset import MediaAsset, MediaDailyUsage, MediaMonthlyBudget
from app.models.user import User
from app.services.media_usage import MediaBudgetExceeded, MediaQuotaExceeded, MediaReservation, reserve_media_usage, release_media_usage
from app.services.object_storage import ObjectStorage

router = APIRouter(prefix="/media")

class GenerateImage(BaseModel):
    prompt: str = Field(min_length=4, max_length=1000)
    conversation_id: UUID | None = None
    size: str = Field(default="1024x1024", pattern="^(1024x1024|1536x1024|1024x1536)$")

class GenerateVoice(BaseModel):
    text: str = Field(min_length=1, max_length=4000)
    conversation_id: UUID | None = None
    voice: str = Field(default="alloy", pattern="^(alloy|ash|coral|echo|fable|onyx|nova|sage|shimmer)$")

async def _owned_conversation(db: AsyncSession, user_id: UUID, conversation_id: UUID | None):
    if conversation_id is None:
        return
    found = await db.scalar(select(Conversation.id).where(Conversation.id == conversation_id, Conversation.user_id == user_id))
    if found is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

async def _generate(user: User, db: AsyncSession, kind: str, prompt: str, conversation_id: UUID | None, size: str | None = None, voice: str | None = None):
    if not settings.openai_api_key or not settings.ai_default_provider or not settings.ai_default_model:
        raise HTTPException(status_code=503, detail="Media generation is not configured")
    await _owned_conversation(db, user.id, conversation_id)
    provider = build_provider(settings.ai_default_provider)
    safety = await provider.moderate(prompt)
    if safety.flagged:
        raise HTTPException(status_code=422, detail="This prompt cannot be used under ALAP safety rules")
    reservation: MediaReservation | None = None
    storage: ObjectStorage | None = None
    object_key: str | None = None
    try:
        reservation = await reserve_media_usage(db, user.id, kind, len(prompt) if kind == "voice" else 0)
    except MediaQuotaExceeded:
        await db.rollback()
        raise HTTPException(status_code=429, detail="Your daily media generation allowance has been reached") from None
    except MediaBudgetExceeded:
        await db.rollback()
        raise HTTPException(status_code=429, detail="ALAP's monthly media budget has been reached; try again next month") from None
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(120, connect=10)) as client:
            if kind == "image":
                response = await client.post("https://api.openai.com/v1/images/generations",
                    headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                    json={"model": settings.image_generation_model, "prompt": prompt, "size": size, "n": 1})
                response.raise_for_status()
                payload = response.json()
                raw = base64.b64decode(payload["data"][0]["b64_json"], validate=True)
                moderation = await client.post("https://api.openai.com/v1/moderations",
                    headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                    json={"model": "omni-moderation-latest", "input": [{"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(raw).decode("ascii")}}]})
                moderation.raise_for_status()
                if moderation.json().get("results", [{}])[0].get("flagged", True):
                    raise HTTPException(status_code=422, detail="Generated image did not pass ALAP safety checks")
                mime, extension, model = "image/png", "png", settings.image_generation_model
            else:
                response = await client.post("https://api.openai.com/v1/audio/speech",
                    headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                    json={"model": settings.voice_generation_model, "input": prompt, "voice": voice, "response_format": "mp3"})
                response.raise_for_status()
                raw, mime, extension, model = response.content, "audio/mpeg", "mp3", settings.voice_generation_model
        if not raw or len(raw) > settings.media_max_bytes:
            raise RuntimeError("Generated media is empty or exceeds the configured size limit")
        asset_id = uuid4()
        object_key = f"users/{user.id}/{kind}/{asset_id}.{extension}"
        storage = ObjectStorage()
        await storage.put(object_key, raw, mime)
        url = await storage.signed_get(object_key)
        asset = MediaAsset(id=asset_id, user_id=user.id, conversation_id=conversation_id, kind=kind,
                           object_key=object_key, mime_type=mime, size_bytes=len(raw), provider="openai", model=model)
        db.add(asset)
        await db.commit()
        return {"id": str(asset.id), "kind": kind, "mime_type": mime, "size_bytes": len(raw), "url": url, "url_expires_in": 300}
    except Exception as exc:
        await db.rollback()
        if storage is not None and object_key is not None:
            try:
                await storage.delete(object_key)
            except Exception:
                pass
        if reservation is not None:
            try:
                await release_media_usage(db, user.id, reservation)
            except Exception:
                await db.rollback()
        if isinstance(exc, HTTPException):
            raise exc
        raise HTTPException(status_code=502, detail="Media generation or private storage failed; the reserved media allowance was released where possible") from exc

@router.post("/images", status_code=status.HTTP_201_CREATED)
async def generate_image(body: GenerateImage, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user),
                         _ip: None = Depends(rate_limit(5, 60)), _account: None = Depends(account_rate_limit(5, 60))):
    return await _generate(user, db, "image", body.prompt, body.conversation_id, size=body.size)

@router.post("/voice", status_code=status.HTTP_201_CREATED)
async def generate_voice(body: GenerateVoice, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user),
                         _ip: None = Depends(rate_limit(10, 60)), _account: None = Depends(account_rate_limit(10, 60))):
    return await _generate(user, db, "voice", body.text, body.conversation_id, voice=body.voice)

@router.get("/usage")
async def media_usage(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    now = datetime.now(timezone.utc)
    daily = await db.scalar(select(MediaDailyUsage).where(
        MediaDailyUsage.user_id == user.id, MediaDailyUsage.usage_date == now.date()
    ))
    monthly = await db.scalar(select(MediaMonthlyBudget).where(MediaMonthlyBudget.month == now.strftime("%Y-%m")))
    return {
        "images_used": daily.image_count if daily else 0,
        "images_limit": settings.media_daily_image_limit,
        "voice_characters_used": daily.voice_characters if daily else 0,
        "voice_characters_limit": settings.media_daily_voice_characters,
        "monthly_estimated_spend_usd": float(monthly.spent_usd) if monthly else 0,
        "monthly_budget_usd": settings.media_monthly_budget_usd,
    }

@router.get("")
async def list_media(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    rows = await db.scalars(select(MediaAsset).where(MediaAsset.user_id == user.id).order_by(MediaAsset.created_at.desc()).limit(100))
    assets = list(rows.all())
    storage = ObjectStorage() if assets else None
    result = []
    for item in assets:
        result.append({"id": str(item.id), "kind": item.kind, "conversation_id": str(item.conversation_id) if item.conversation_id else None,
                       "mime_type": item.mime_type, "size_bytes": item.size_bytes, "created_at": item.created_at,
                       "url": await storage.signed_get(item.object_key) if storage else None, "url_expires_in": 300})
    return result

@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media(asset_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    asset = await db.scalar(select(MediaAsset).where(MediaAsset.id == asset_id, MediaAsset.user_id == user.id))
    if asset is None:
        raise HTTPException(status_code=404, detail="Media asset not found")
    try:
        await ObjectStorage().delete(asset.object_key)
    except Exception:
        raise HTTPException(status_code=503, detail="Private storage is unavailable; media metadata was not deleted") from None
    await db.delete(asset)
    await db.commit()

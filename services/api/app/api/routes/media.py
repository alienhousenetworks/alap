import secrets
from datetime import datetime, timezone
from uuid import UUID
import httpx
from botocore.exceptions import BotoCoreError
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import account_rate_limit, get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.media_asset import MediaAsset
from app.models.user import User
from app.schemas.media import ImageGenerationRequest, MediaAssetResponse, MediaUrlResponse, SpeechGenerationRequest
from app.services.media_generation import generate_image, generate_speech, moderate_image, moderate_text
from app.services.media_storage import delete_object, signed_object_url, store_object

router = APIRouter(prefix="/media")


async def _consume_daily_quota(request: Request, user_id: UUID, media_type: str, limit: int):
    key = f"media-quota:{media_type}:{user_id}:{datetime.now(timezone.utc).date().isoformat()}"
    try:
        count = await request.app.state.redis.incr(key)
        if count == 1:
            await request.app.state.redis.expire(key, 90000)
    except Exception:
        raise HTTPException(status_code=503, detail="Usage quota service is unavailable") from None
    if count > limit:
        raise HTTPException(status_code=429, detail="Daily media generation limit reached")


@router.post("/images", response_model=MediaAssetResponse, status_code=status.HTTP_201_CREATED)
async def create_image(
    body: ImageGenerationRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    _: None = Depends(account_rate_limit(10, 60)),
):
    await _consume_daily_quota(request, user.id, "image", settings.media_image_daily_limit)
    try:
        safety = await moderate_text(body.prompt)
        if safety.flagged:
            raise HTTPException(status_code=422, detail="Image prompt did not pass safety checks")
        image_bytes = await generate_image(body.prompt)
        image_safety = await moderate_image(image_bytes)
        if image_safety.flagged:
            raise HTTPException(status_code=502, detail="Generated image did not pass safety checks")
        key = f"users/{user.id}/images/{secrets.token_hex(16)}.png"
        await store_object(key=key, body=image_bytes, content_type="image/png")
    except HTTPException:
        raise
    except (httpx.HTTPError, RuntimeError, ValueError, BotoCoreError):
        raise HTTPException(status_code=502, detail="Image generation or secure storage is unavailable") from None
    asset = MediaAsset(
        user_id=user.id, media_type="image", object_key=key, mime_type="image/png",
        byte_size=len(image_bytes), provider="openai", model=settings.media_image_model,
    )
    db.add(asset)
    await db.commit()
    await db.refresh(asset)
    return asset


@router.post("/speech", response_model=MediaAssetResponse, status_code=status.HTTP_201_CREATED)
async def create_speech(
    body: SpeechGenerationRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    _: None = Depends(account_rate_limit(20, 60)),
):
    await _consume_daily_quota(request, user.id, "speech", settings.media_speech_daily_limit)
    try:
        safety = await moderate_text(body.text)
        if safety.flagged:
            raise HTTPException(status_code=422, detail="Speech text did not pass safety checks")
        audio_bytes = await generate_speech(body.text, body.voice)
        key = f"users/{user.id}/audio/{secrets.token_hex(16)}.mp3"
        await store_object(key=key, body=audio_bytes, content_type="audio/mpeg")
    except HTTPException:
        raise
    except (httpx.HTTPError, RuntimeError, ValueError, BotoCoreError):
        raise HTTPException(status_code=502, detail="Speech generation or secure storage is unavailable") from None
    asset = MediaAsset(
        user_id=user.id, media_type="audio", object_key=key, mime_type="audio/mpeg",
        byte_size=len(audio_bytes), provider="openai", model=settings.media_tts_model,
    )
    db.add(asset)
    await db.commit()
    await db.refresh(asset)
    return asset


@router.get("", response_model=list[MediaAssetResponse])
async def list_media(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    rows = await db.scalars(select(MediaAsset).where(MediaAsset.user_id == user.id).order_by(MediaAsset.created_at.desc()).limit(100))
    return list(rows.all())


@router.get("/{asset_id}/url", response_model=MediaUrlResponse)
async def get_media_url(asset_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    asset = await db.scalar(select(MediaAsset).where(MediaAsset.id == asset_id, MediaAsset.user_id == user.id))
    if asset is None:
        raise HTTPException(status_code=404, detail="Media asset not found")
    try:
        url = await signed_object_url(asset.object_key)
    except (RuntimeError, BotoCoreError):
        raise HTTPException(status_code=503, detail="Private media storage is unavailable") from None
    return {"url": url, "expires_in": 900}


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_media(asset_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    asset = await db.scalar(select(MediaAsset).where(MediaAsset.id == asset_id, MediaAsset.user_id == user.id))
    if asset is None:
        raise HTTPException(status_code=404, detail="Media asset not found")
    try:
        await delete_object(asset.object_key)
    except (RuntimeError, BotoCoreError):
        raise HTTPException(status_code=503, detail="Private media storage is unavailable") from None
    await db.delete(asset)
    await db.commit()

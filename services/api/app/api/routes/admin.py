from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import require_admin
from app.db.session import get_db
from app.models.character import Character
from app.models.moderation_audit import ModerationAuditLog
from app.models.user import User
from app.schemas.character import CharacterResponse
from app.schemas.moderation import ModerationAuditResponse, ModerationDecision

router = APIRouter(prefix="/admin")


@router.get("/moderation/characters", response_model=list[CharacterResponse])
async def moderation_queue(
    status: str = Query(default="pending", pattern="^(pending|approved|rejected)$"),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    rows = await db.scalars(
        select(Character)
        .where(Character.moderation_status == status)
        .order_by(Character.created_at.asc())
        .limit(limit)
    )
    return list(rows.all())


@router.get("/audit/moderation", response_model=list[ModerationAuditResponse])
async def moderation_audit(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    rows = await db.scalars(
        select(ModerationAuditLog)
        .order_by(ModerationAuditLog.created_at.desc(), ModerationAuditLog.id.desc())
        .offset(offset)
        .limit(limit)
    )
    return list(rows.all())


@router.post("/characters/{character_id}/approve", response_model=CharacterResponse)
async def approve_character(
    character_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    character = await db.get(Character, character_id, with_for_update=True)
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    character.moderation_status = "approved"
    character.moderation_note = None
    character.is_published = character.visibility == "public"
    db.add(ModerationAuditLog(
        actor_user_id=admin.id,
        character_id=character.id,
        action="approved",
        reason="Approved by moderator",
    ))
    await db.commit()
    await db.refresh(character)
    return character


@router.post("/characters/{character_id}/reject", response_model=CharacterResponse)
async def reject_character(
    character_id: UUID,
    body: ModerationDecision,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    character = await db.get(Character, character_id, with_for_update=True)
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    reason = body.reason.strip() or "Rejected by moderation"
    character.moderation_status = "rejected"
    character.moderation_note = reason
    character.is_published = False
    db.add(ModerationAuditLog(
        actor_user_id=admin.id,
        character_id=character.id,
        action="rejected",
        reason=reason,
    ))
    await db.commit()
    await db.refresh(character)
    return character

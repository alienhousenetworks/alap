from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import require_admin
from app.db.session import get_db
from app.models.character import Character
from app.models.character_report import CharacterReport
from app.models.moderation_audit import ModerationAuditLog
from app.models.user import User
from app.schemas.character import CharacterResponse
from app.schemas.moderation import CharacterReportResponse, ModerationAuditResponse, ModerationDecision, ReportResolution

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


@router.get("/reports", response_model=list[CharacterReportResponse])
async def character_reports(
    status: str = Query(default="open", pattern="^(open|resolved|dismissed)$"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    rows = await db.scalars(
        select(CharacterReport)
        .where(CharacterReport.status == status)
        .order_by(CharacterReport.created_at.asc(), CharacterReport.id.asc())
        .offset(offset)
        .limit(limit)
    )
    return list(rows.all())


@router.post("/reports/{report_id}/resolve", response_model=CharacterReportResponse)
async def resolve_character_report(
    report_id: UUID,
    body: ReportResolution,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    report = await db.get(CharacterReport, report_id, with_for_update=True)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    if report.status != "open":
        raise HTTPException(status_code=409, detail="Report has already been reviewed")
    report.status = body.status
    report.resolution_note = body.note.strip() or None
    report.reviewed_by = admin.id
    report.reviewed_at = datetime.now(timezone.utc)
    db.add(ModerationAuditLog(
        actor_user_id=admin.id,
        character_id=report.character_id,
        action=f"report_{body.status}",
        reason=report.resolution_note or f"Report {body.status}",
    ))
    await db.commit()
    await db.refresh(report)
    return report


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

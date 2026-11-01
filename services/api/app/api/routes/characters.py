from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import account_rate_limit, get_current_user, rate_limit
from app.db.session import get_db
from app.models.character import Character
from app.models.character_report import CharacterReport
from app.models.user import User
from app.schemas.character import CharacterCreate, CharacterUpdate, CharacterResponse
from app.schemas.moderation import CharacterReportCreate, CharacterReportResponse

router = APIRouter(prefix="/characters")

@router.get("/discover", response_model=list[CharacterResponse])
async def discover_characters(
    limit: int = Query(default=24, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = select(Character).where(Character.is_published.is_(True), Character.visibility == "public", Character.moderation_status == "approved").order_by(Character.created_at.desc()).offset(offset).limit(limit)
    return list((await db.scalars(query)).all())

@router.get("/mine", response_model=list[CharacterResponse])
async def my_characters(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.scalars(select(Character).where(Character.owner_id == user.id).order_by(Character.created_at.desc()))
    return list(result.all())

@router.post("", response_model=CharacterResponse, status_code=status.HTTP_201_CREATED)
async def create_character(body: CharacterCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    if len(body.personality) > 30 or any(len(k) > 40 or len(v) > 500 for k, v in body.personality.items()):
        raise HTTPException(status_code=422, detail="Personality fields exceed allowed limits")
    character = Character(owner_id=user.id, **body.model_dump())
    db.add(character)
    await db.commit()
    await db.refresh(character)
    return character

@router.post("/{character_id}/report", response_model=CharacterReportResponse, status_code=status.HTTP_201_CREATED)
async def report_character(
    character_id: UUID,
    body: CharacterReportCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    _ip_limit: None = Depends(rate_limit(5, 60)),
    _account_limit: None = Depends(account_rate_limit(5, 60)),
):
    character = await db.get(Character, character_id)
    if (
        character is None
        or character.owner_id == user.id
        or not character.is_published
        or character.visibility != "public"
        or character.moderation_status != "approved"
    ):
        raise HTTPException(status_code=404, detail="Character not found")
    existing = await db.scalar(
        select(CharacterReport).where(
            CharacterReport.reporter_user_id == user.id,
            CharacterReport.character_id == character.id,
            CharacterReport.status == "open",
        )
    )
    if existing is not None:
        raise HTTPException(status_code=409, detail="You already have an open report for this character")
    report = CharacterReport(
        reporter_user_id=user.id,
        character_id=character.id,
        reason=body.reason,
        details=body.details.strip() or None,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report


@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(character_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    character = await db.get(Character, character_id)
    if character is None or not (character.owner_id == user.id or (character.is_published and character.visibility == "public" and character.moderation_status == "approved")):
        raise HTTPException(status_code=404, detail="Character not found")
    return character

@router.patch("/{character_id}", response_model=CharacterResponse)
async def update_character(character_id: UUID, body: CharacterUpdate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    character = await db.get(Character, character_id)
    if character is None or character.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Character not found")
    changes = body.model_dump(exclude_unset=True)
    if any(value is None for value in changes.values()):
        raise HTTPException(status_code=422, detail="Character fields cannot be set to null")
    personality = changes.get("personality")
    if personality is not None and (len(personality) > 30 or any(len(k) > 40 or len(v) > 500 for k, v in personality.items())):
        raise HTTPException(status_code=422, detail="Personality fields exceed allowed limits")
    for key, value in changes.items():
        setattr(character, key, value)
    if changes:
        # Any owner edit invalidates the prior safety review before republishing.
        character.moderation_status = "pending"
        character.moderation_note = None
        character.is_published = False
    await db.commit()
    await db.refresh(character)
    return character

@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character(character_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    character = await db.get(Character, character_id)
    if character is None or character.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Character not found")
    await db.delete(character)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

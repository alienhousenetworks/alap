from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.character import Character
from app.models.user import User
from app.schemas.character import CharacterCreate, CharacterUpdate, CharacterResponse

router = APIRouter(prefix="/characters")

@router.get("/discover", response_model=list[CharacterResponse])
async def discover_characters(
    limit: int = Query(default=24, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = select(Character).where(Character.is_published.is_(True), Character.visibility == "public").order_by(Character.created_at.desc()).offset(offset).limit(limit)
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

@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(character_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    character = await db.get(Character, character_id)
    if character is None or not (character.owner_id == user.id or (character.is_published and character.visibility == "public")):
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

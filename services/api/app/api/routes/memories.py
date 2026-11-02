from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.character import Character
from app.models.memory import CharacterMemory
from app.models.user import User
from app.schemas.memory import MemoryCreate, MemoryPreferenceUpdate, MemoryResponse
from app.services.memory import encrypt_memory, list_memories, _fingerprint

router = APIRouter(prefix="/characters/{character_id}/memory")


async def _accessible_character(db: AsyncSession, user: User, character_id: UUID):
    character = await db.scalar(select(Character).where(Character.id == character_id))
    if character is None or not (
        character.owner_id == user.id
        or (character.is_published and character.visibility == "public" and character.moderation_status == "approved")
    ):
        raise HTTPException(status_code=404, detail="Character not found")
    return character


@router.get("", response_model=list[MemoryResponse])
async def get_memory(character_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    await _accessible_character(db, user, character_id)
    return await list_memories(db, user_id=user.id, character_id=character_id)


@router.post("", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
async def create_memory(character_id: UUID, body: MemoryCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    await _owned_character(db, user, character_id)
    if not user.memory_enabled:
        raise HTTPException(status_code=409, detail="Enable long-term memory before adding memories")
    if not settings.memory_encryption_key:
        raise HTTPException(status_code=503, detail="Memory encryption is not configured")
    row = CharacterMemory(
        user_id=user.id, character_id=character_id, category=body.category,
        encrypted_content=encrypt_memory(body.content), fingerprint=_fingerprint(body.content),
        importance=body.importance,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return {"id": row.id, "category": row.category, "content": body.content, "importance": row.importance, "created_at": row.created_at, "updated_at": row.updated_at}


@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory(character_id: UUID, memory_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    await _owned_character(db, user, character_id)
    row = await db.scalar(select(CharacterMemory).where(
        CharacterMemory.id == memory_id, CharacterMemory.user_id == user.id, CharacterMemory.character_id == character_id
    ))
    if row is None:
        raise HTTPException(status_code=404, detail="Memory not found")
    await db.delete(row)
    await db.commit()


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def clear_memory(character_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    await _owned_character(db, user, character_id)
    await db.execute(delete(CharacterMemory).where(CharacterMemory.user_id == user.id))
    await db.commit()

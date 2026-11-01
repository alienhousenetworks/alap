import httpx
from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.ai.protocol import ChatMessage
from app.ai.registry import build_provider
from app.api.deps import get_current_user, rate_limit
from app.core.config import settings
from app.db.session import get_db
from app.models.character import Character
from app.models.conversation import Conversation, ConversationMessage
from app.models.user import User
from app.schemas.conversation import ConversationCreate, ConversationResponse, MessageCreate, MessageResponse, ChatTurnResponse

router = APIRouter(prefix="/conversations")

@router.get("", response_model=list[ConversationResponse])
async def list_conversations(limit: int = Query(default=30, ge=1, le=100), offset: int = Query(default=0, ge=0), db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    rows = await db.scalars(select(Conversation).where(Conversation.user_id == user.id).order_by(Conversation.updated_at.desc()).offset(offset).limit(limit))
    return list(rows.all())

@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(body: ConversationCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    character = await db.get(Character, body.character_id)
    if character is None or not (character.owner_id == user.id or (character.is_published and character.visibility == "public" and character.moderation_status == "approved")):
        raise HTTPException(status_code=404, detail="Character not found")
    conversation = Conversation(user_id=user.id, character_id=character.id, title=character.name)
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    return conversation

@router.get("/{conversation_id}/messages", response_model=list[MessageResponse])
async def list_messages(conversation_id: UUID, limit: int = Query(default=50, ge=1, le=100), before_id: UUID | None = None, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    conversation = await db.scalar(select(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == user.id))
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    query = select(ConversationMessage).where(ConversationMessage.conversation_id == conversation_id).order_by(ConversationMessage.created_at.desc()).limit(limit)
    if before_id is not None:
        cursor = await db.get(ConversationMessage, before_id)
        if cursor is None or cursor.conversation_id != conversation_id:
            raise HTTPException(status_code=400, detail="Invalid message cursor")
        query = query.where(ConversationMessage.created_at < cursor.created_at)
    rows = list((await db.scalars(query)).all())
    return list(reversed(rows))

@router.post("/{conversation_id}/messages", response_model=ChatTurnResponse)
async def send_message(conversation_id: UUID, body: MessageCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user), _: None = Depends(rate_limit(20, 60))):
    conversation = await db.scalar(select(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == user.id).with_for_update())
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    character = await db.get(Character, conversation.character_id)
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    if not settings.ai_default_provider or not settings.ai_default_model:
        raise HTTPException(status_code=503, detail="AI generation is not configured")
    previous = list((await db.scalars(select(ConversationMessage).where(ConversationMessage.conversation_id == conversation_id).order_by(ConversationMessage.created_at.desc()).limit(20))).all())
    previous.reverse()
    persona = f"You are roleplaying as {character.name}. Stay consistent with this fictional character. Description: {character.description}. Personality: {character.personality}. Keep responses engaging and respectful. Do not claim to be a real person."
    messages = [ChatMessage(role="system", content=persona)]
    messages.extend(ChatMessage(role=item.role, content=item.content) for item in previous if item.role in {"user", "assistant"})
    messages.append(ChatMessage(role="user", content=body.content))
    try:
        provider = build_provider(settings.ai_default_provider)
        result = await provider.generate(model=settings.ai_default_model, messages=messages, temperature=0.8, max_tokens=700)
    except (ValueError, httpx.HTTPError, RuntimeError):
        raise HTTPException(status_code=502, detail="AI provider is unavailable; your message was not saved") from None
    user_message = ConversationMessage(conversation_id=conversation_id, role="user", content=body.content)
    assistant_message = ConversationMessage(conversation_id=conversation_id, role="assistant", content=result.text, provider=result.provider, model=result.model, input_tokens=result.input_tokens, output_tokens=result.output_tokens)
    conversation.updated_at = datetime.now(timezone.utc)
    db.add_all([user_message, assistant_message])
    await db.commit()
    await db.refresh(user_message)
    await db.refresh(assistant_message)
    await db.refresh(conversation)
    return ChatTurnResponse(conversation=conversation, user_message=user_message, assistant_message=assistant_message)

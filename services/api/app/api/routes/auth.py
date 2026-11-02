import uuid
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, rate_limit
from app.core.config import settings
from app.core.security import create_token, decode_token, hash_password, verify_password
from app.db.session import get_db
from app.models.auth_session import AuthSession
from app.models.character import Character
from app.models.conversation import Conversation, ConversationMessage
from app.models.user import User
from app.models.media_asset import MediaAsset
from app.services.media_storage import delete_user_objects
from app.schemas.auth import DeleteAccountRequest, LoginRequest, RefreshRequest, RegisterRequest, TokenResponse, UserResponse
from app.schemas.character import CharacterResponse
from app.schemas.conversation import ConversationResponse, MessageResponse

router = APIRouter(prefix="/auth")

def issue_tokens(user: User):
    now = datetime.now(timezone.utc)
    jti = str(uuid.uuid4())
    expiry = now + timedelta(days=settings.refresh_token_ttl_days)
    access = create_token(str(user.id), "access", timedelta(minutes=settings.access_token_ttl_minutes))
    refresh = create_token(str(user.id), "refresh", timedelta(days=settings.refresh_token_ttl_days), jti=jti)
    return access, refresh, jti, expiry

async def persist_session(db: AsyncSession, user: User, jti: str, expiry: datetime):
    db.add(AuthSession(user_id=user.id, refresh_jti=jti, expires_at=expiry))

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db), _: None = Depends(rate_limit(5, 60))):
    if not body.confirm_adult:
        raise HTTPException(status_code=400, detail="You must confirm that you meet the age requirement")
    email = str(body.email).strip().lower()
    user = User(email=email, password_hash=hash_password(body.password), display_name=body.display_name.strip(), is_adult_confirmed=True)
    db.add(user)
    try:
        await db.flush()
        access, refresh, jti, expiry = issue_tokens(user)
        await persist_session(db, user, jti, expiry)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="An account with this email already exists") from None
    return TokenResponse(access_token=access, refresh_token=refresh, expires_in=settings.access_token_ttl_minutes * 60)

@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db), _: None = Depends(rate_limit(10, 60))):
    email = str(body.email).strip().lower()
    user = await db.scalar(select(User).where(User.email == email, User.is_active.is_(True)))
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email or password is incorrect")
    access, refresh, jti, expiry = issue_tokens(user)
    await persist_session(db, user, jti, expiry)
    await db.commit()
    return TokenResponse(access_token=access, refresh_token=refresh, expires_in=settings.access_token_ttl_minutes * 60)

@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_token(body.refresh_token, expected_type="refresh")
        user_id, jti = uuid.UUID(payload["sub"]), payload["jti"]
    except (ValueError, KeyError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token") from None
    session = await db.scalar(select(AuthSession).where(AuthSession.refresh_jti == jti).with_for_update())
    now = datetime.now(timezone.utc)
    if session is None or session.revoked or session.expires_at <= now or session.user_id != user_id:
        raise HTTPException(status_code=401, detail="Refresh token is no longer valid")
    user = await db.scalar(select(User).where(User.id == user_id, User.is_active.is_(True)))
    if user is None:
        raise HTTPException(status_code=401, detail="Account is inactive")
    session.revoked = True
    access, new_refresh, new_jti, expiry = issue_tokens(user)
    await persist_session(db, user, new_jti, expiry)
    await db.commit()
    return TokenResponse(access_token=access, refresh_token=new_refresh, expires_in=settings.access_token_ttl_minutes * 60)

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_token(body.refresh_token, expected_type="refresh")
        jti = payload["jti"]
    except (ValueError, KeyError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid refresh token") from None
    session = await db.scalar(select(AuthSession).where(AuthSession.refresh_jti == jti))
    if session is not None:
        session.revoked = True
        await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)):
    return user

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(body: DeleteAccountRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    if not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=403, detail="Password confirmation failed")
    media_rows = list((await db.scalars(select(MediaAsset).where(MediaAsset.user_id == user.id))).all())
    if media_rows:
        try:
            await delete_user_objects([item.object_key for item in media_rows])
        except Exception:
            raise HTTPException(status_code=503, detail="Account deletion is paused because private media could not be securely purged") from None
    await db.delete(user)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me/export")
async def export_account_data(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    _: None = Depends(rate_limit(5, 60)),
):
    characters = list((await db.scalars(
        select(Character).where(Character.owner_id == user.id).order_by(Character.created_at.asc())
    )).all())
    conversations = list((await db.scalars(
        select(Conversation).where(Conversation.user_id == user.id).order_by(Conversation.created_at.asc())
    )).all())
    conversation_ids = [item.id for item in conversations]
    messages = []
    if conversation_ids:
        messages = list((await db.scalars(
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id.in_(conversation_ids))
            .order_by(ConversationMessage.created_at.asc(), ConversationMessage.id.asc())
        )).all())
    return {
        "export_format_version": 1,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "account": UserResponse.model_validate(user).model_dump(mode="json"),
        "characters": [CharacterResponse.model_validate(item).model_dump(mode="json") for item in characters],
        "conversations": [ConversationResponse.model_validate(item).model_dump(mode="json") for item in conversations],
        "messages": [MessageResponse.model_validate(item).model_dump(mode="json") for item in messages],
    }

import uuid
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.core.config import settings
from app.core.security import create_token, decode_token, hash_password, verify_password
from app.db.session import get_db
from app.models.auth_session import AuthSession
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse, UserResponse

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
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
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
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
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
async def logout(body: RefreshRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        payload = decode_token(body.refresh_token, expected_type="refresh")
        jti = payload["jti"]
    except (ValueError, KeyError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid refresh token") from None
    session = await db.scalar(select(AuthSession).where(AuthSession.refresh_jti == jti, AuthSession.user_id == user.id))
    if session is not None:
        session.revoked = True
        await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)):
    return user

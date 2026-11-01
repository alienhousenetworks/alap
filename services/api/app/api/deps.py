from uuid import UUID
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis.exceptions import RedisError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User

bearer = HTTPBearer(auto_error=False)

async def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: AsyncSession = Depends(get_db)) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    try:
        payload = decode_token(credentials.credentials, expected_type="access")
        user_id = UUID(payload["sub"])
    except (ValueError, KeyError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid or expired access token") from None
    user = await db.scalar(select(User).where(User.id == user_id, User.is_active.is_(True)))
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or inactive account")
    return user

def rate_limit(max_requests: int, window_seconds: int):
    async def dependency(request: Request):
        client = request.client.host if request.client else "unknown"
        key = f"ratelimit:{request.url.path}:{client}"
        try:
            pipe = request.app.state.redis.pipeline()
            pipe.incr(key)
            pipe.ttl(key)
            count, ttl = await pipe.execute()
            if count == 1 or ttl < 0:
                await request.app.state.redis.expire(key, window_seconds)
        except RedisError:
            raise HTTPException(status_code=503, detail="Rate limiting service is unavailable") from None
        if count > max_requests:
            raise HTTPException(status_code=429, detail="Too many requests. Please try again later.", headers={"Retry-After": str(max(1, ttl))})
    return dependency

async def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Administrator access required")
    return user

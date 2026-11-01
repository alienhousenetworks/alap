from datetime import datetime, timedelta, timezone
from uuid import uuid4
import jwt
from jwt import InvalidTokenError
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from app.core.config import settings

_password_hasher = PasswordHasher()

def hash_password(password: str) -> str:
    if len(password) < 12:
        raise ValueError("Password must contain at least 12 characters")
    return _password_hasher.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _password_hasher.verify(password_hash, password)
    except VerificationError:
        return False

def create_token(subject: str, token_type: str, lifetime: timedelta, jti: str | None = None) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": subject, "iat": now, "exp": now + lifetime, "type": token_type, "jti": jti or str(uuid4())}
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")

def decode_token(token: str, expected_type: str) -> dict:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"], options={"require": ["exp", "iat", "sub", "type"]})
    except InvalidTokenError as exc:
        raise ValueError("Invalid or expired token") from exc
    if payload.get("type") != expected_type:
        raise ValueError("Wrong token type")
    return payload

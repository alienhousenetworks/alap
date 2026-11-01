from datetime import timedelta
import pytest
from app.core.security import create_token, decode_token, hash_password, verify_password

def test_password_hash_is_not_plaintext_and_verifies():
    raw = "correct-horse-battery-staple"
    hashed = hash_password(raw)
    assert hashed != raw
    assert verify_password(raw, hashed)
    assert not verify_password("wrong-password-value", hashed)

def test_password_policy_rejects_short_password():
    with pytest.raises(ValueError):
        hash_password("short")

def test_token_type_is_enforced():
    token = create_token("user-123", "access", timedelta(minutes=5))
    assert decode_token(token, "access")["sub"] == "user-123"
    with pytest.raises(ValueError):
        decode_token(token, "refresh")

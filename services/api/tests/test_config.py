import pytest
from pydantic import ValidationError
from app.core.config import Settings


def valid_production_settings(**overrides):
    values = {
        "app_env": "production",
        "jwt_secret": "r" * 48,
        "database_url": "postgresql+asyncpg://alap:secret@db.internal:5432/alap",
        "cors_origins": "https://app.example.com,https://admin.example.com",
        "ai_default_provider": "anthropic",
        "ai_default_model": "claude-model",
        "openai_api_key": "moderation-key",
        "anthropic_api_key": "anthropic-key",
        "object_storage_bucket": "alap-media",
        "object_storage_access_key": "access",
        "object_storage_secret_key": "secret",
        "media_monthly_budget_usd": 100,
        "media_image_estimated_cost_usd": 0.05,
        "media_voice_estimated_cost_per_1k_chars_usd": 0.02,
    }
    values.update(overrides)
    return Settings(**values)


def test_production_configuration_accepts_explicit_secure_values():
    settings = valid_production_settings()
    assert settings.app_env == "production"


def test_production_configuration_rejects_placeholder_secret():
    with pytest.raises(ValidationError):
        valid_production_settings(jwt_secret="replace-with-at-least-32-random-characters")


def test_production_configuration_requires_moderation_provider():
    with pytest.raises(ValidationError):
        valid_production_settings(openai_api_key="")


def test_production_configuration_requires_selected_provider_key():
    with pytest.raises(ValidationError):
        valid_production_settings(anthropic_api_key="")

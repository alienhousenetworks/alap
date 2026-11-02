from functools import lru_cache
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from cryptography.fernet import Fernet

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    app_env: str = "development"
    app_name: str = "ALAP API"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+asyncpg://alap:change-me@localhost:5432/alap"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "development-only-change-this-secret"
    access_token_ttl_minutes: int = 15
    refresh_token_ttl_days: int = 30
    cors_origins: str = "http://localhost:3000"
    log_level: str = "INFO"
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    google_ai_api_key: str = ""
    ai_default_provider: str = ""
    ai_default_model: str = ""
    memory_encryption_key: str = ""
    memory_extraction_model: str = ""
    media_s3_endpoint: str = ""
    media_s3_bucket: str = ""
    media_s3_access_key: str = ""
    media_s3_secret_key: str = ""
    media_s3_region: str = "us-east-1"
    media_image_model: str = "gpt-image-1"
    media_tts_model: str = "tts-1"
    media_image_daily_limit: int = 5
    media_speech_daily_limit: int = 30

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @model_validator(mode="after")
    def enforce_production_secrets(self):
        if self.app_env.lower() == "production":
            weak_secret_markers = ("development-only", "replace-with-", "change-me", "example", "test-only")
            if len(self.jwt_secret) < 32 or any(marker in self.jwt_secret.lower() for marker in weak_secret_markers):
                raise ValueError("Production requires a unique randomly generated JWT_SECRET of at least 32 characters")
            if "change-me" in self.database_url or "localhost" in self.database_url:
                raise ValueError("Production DATABASE_URL must use a managed/private database host")
            if not self.allowed_origins or any("localhost" in origin for origin in self.allowed_origins):
                raise ValueError("Production CORS_ORIGINS must contain explicit HTTPS application origins")
            if any(not origin.startswith("https://") for origin in self.allowed_origins):
                raise ValueError("Production CORS origins must use HTTPS")
            if not self.ai_default_provider or not self.ai_default_model:
                raise ValueError("Production requires an explicit AI_DEFAULT_PROVIDER and AI_DEFAULT_MODEL")
            if not self.openai_api_key:
                raise ValueError("Production requires OPENAI_API_KEY for mandatory content moderation")
            provider_keys = {
                "openai": self.openai_api_key,
                "anthropic": self.anthropic_api_key,
                "google": self.google_ai_api_key,
                "gemini": self.google_ai_api_key,
            }
            if self.ai_default_provider.lower() not in provider_keys:
                raise ValueError("AI_DEFAULT_PROVIDER must be openai, anthropic or google")
            if not provider_keys[self.ai_default_provider.lower()]:
                raise ValueError("The selected AI provider API key is not configured")
            if not self.memory_encryption_key:
                raise ValueError("Production requires MEMORY_ENCRYPTION_KEY for user-controlled long-term memory")
            try:
                Fernet(self.memory_encryption_key.encode("ascii"))
            except (ValueError, TypeError):
                raise ValueError("MEMORY_ENCRYPTION_KEY must be a valid Fernet key") from None
            if not all([self.media_s3_bucket, self.media_s3_access_key, self.media_s3_secret_key]):
                raise ValueError("Production requires private S3-compatible media storage credentials and bucket")
            if self.media_image_daily_limit < 1 or self.media_speech_daily_limit < 1:
                raise ValueError("Media daily limits must be positive")
        if not 5 <= self.access_token_ttl_minutes <= 60:
            raise ValueError("ACCESS_TOKEN_TTL_MINUTES must be between 5 and 60")
        if not 1 <= self.refresh_token_ttl_days <= 90:
            raise ValueError("REFRESH_TOKEN_TTL_DAYS must be between 1 and 90")
        return self

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()

from functools import lru_cache
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

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
    image_generation_model: str = "gpt-image-1"
    voice_generation_model: str = "gpt-4o-mini-tts"
    media_max_bytes: int = 20000000
    media_daily_image_limit: int = 5
    media_daily_voice_characters: int = 10000
    media_monthly_budget_usd: float = 0
    media_image_estimated_cost_usd: float = 0
    media_voice_estimated_cost_per_1k_chars_usd: float = 0
    object_storage_endpoint: str = ""
    object_storage_region: str = "us-east-1"
    object_storage_bucket: str = ""
    object_storage_access_key: str = ""
    object_storage_secret_key: str = ""

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
            storage_values = (self.object_storage_bucket, self.object_storage_access_key, self.object_storage_secret_key)
            if not all(storage_values):
                raise ValueError("Production requires private S3-compatible object storage")
            if self.object_storage_endpoint and not self.object_storage_endpoint.startswith("https://"):
                raise ValueError("Production object storage endpoint must use HTTPS")
            if self.media_monthly_budget_usd <= 0 or self.media_image_estimated_cost_usd <= 0 or self.media_voice_estimated_cost_per_1k_chars_usd <= 0:
                raise ValueError("Production requires positive media monthly budget and provider cost estimates")
        if not 1 <= self.media_daily_image_limit <= 100 or not 100 <= self.media_daily_voice_characters <= 100000:
            raise ValueError("Media daily limits are outside safe bounds")
        if not 1000000 <= self.media_max_bytes <= 100000000:
            raise ValueError("MEDIA_MAX_BYTES must be between 1 MB and 100 MB")
        if not 5 <= self.access_token_ttl_minutes <= 60:
            raise ValueError("ACCESS_TOKEN_TTL_MINUTES must be between 5 and 60")
        if not 1 <= self.refresh_token_ttl_days <= 90:
            raise ValueError("REFRESH_TOKEN_TTL_DAYS must be between 1 and 90")
        return self

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()

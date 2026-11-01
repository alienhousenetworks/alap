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

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @model_validator(mode="after")
    def enforce_production_secrets(self):
        if self.app_env.lower() == "production":
            if len(self.jwt_secret) < 32 or self.jwt_secret == "development-only-change-this-secret":
                raise ValueError("Production requires a unique JWT_SECRET of at least 32 characters")
            if "change-me" in self.database_url or "localhost" in self.database_url:
                raise ValueError("Production DATABASE_URL must use a managed/private database host")
            if not self.allowed_origins or any("localhost" in origin for origin in self.allowed_origins):
                raise ValueError("Production CORS_ORIGINS must contain explicit HTTPS application origins")
            if any(not origin.startswith("https://") for origin in self.allowed_origins):
                raise ValueError("Production CORS origins must use HTTPS")
        if not 5 <= self.access_token_ttl_minutes <= 60:
            raise ValueError("ACCESS_TOKEN_TTL_MINUTES must be between 5 and 60")
        if not 1 <= self.refresh_token_ttl_days <= 90:
            raise ValueError("REFRESH_TOKEN_TTL_DAYS must be between 1 and 90")
        return self

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()

from app.ai.openai_compatible import OpenAICompatibleProvider
from app.core.config import settings


def build_provider(name: str):
    normalized = name.strip().lower()
    if normalized == "openai":
        return OpenAICompatibleProvider(settings.openai_api_key)
    raise ValueError(f"Provider '{name}' is not configured or supported")

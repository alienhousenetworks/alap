from app.ai.anthropic import AnthropicProvider
from app.ai.google import GoogleAIProvider
from app.ai.openai_compatible import OpenAICompatibleProvider
from app.ai.protocol import ChatMessage, GenerationResult, ModerationResult
from app.core.config import settings


class ModeratedProvider:
    """Combines a selected generation provider with the mandatory OpenAI safety service."""

    def __init__(self, generation_provider, moderation_provider):
        self.generation_provider = generation_provider
        self.moderation_provider = moderation_provider

    async def generate(
        self, *, model: str, messages: list[ChatMessage], temperature: float = 0.8,
        max_tokens: int = 700,
    ) -> GenerationResult:
        return await self.generation_provider.generate(
            model=model, messages=messages, temperature=temperature, max_tokens=max_tokens
        )

    async def moderate(self, text: str) -> ModerationResult:
        return await self.moderation_provider.moderate(text)


def build_provider(name: str):
    normalized = name.strip().lower()
    if normalized == "openai":
        generation = OpenAICompatibleProvider(settings.openai_api_key)
    elif normalized == "anthropic":
        generation = AnthropicProvider(settings.anthropic_api_key)
    elif normalized in {"google", "gemini"}:
        generation = GoogleAIProvider(settings.google_ai_api_key)
    else:
        raise ValueError(f"Provider '{name}' is not configured or supported")
    moderation = (
        generation
        if isinstance(generation, OpenAICompatibleProvider)
        else OpenAICompatibleProvider(settings.openai_api_key)
    )
    return ModeratedProvider(generation, moderation)

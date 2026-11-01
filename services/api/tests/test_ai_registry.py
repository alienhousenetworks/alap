from app.ai.registry import ModeratedProvider, build_provider
from app.core.config import settings


def test_anthropic_provider_requires_moderation_key(monkeypatch):
    monkeypatch.setattr(settings, "anthropic_api_key", "anthropic-test-key")
    monkeypatch.setattr(settings, "openai_api_key", "moderation-test-key")
    provider = build_provider("anthropic")
    assert isinstance(provider, ModeratedProvider)
    assert provider.generation_provider.__class__.__name__ == "AnthropicProvider"


def test_google_provider_requires_moderation_key(monkeypatch):
    monkeypatch.setattr(settings, "google_ai_api_key", "google-test-key")
    monkeypatch.setattr(settings, "openai_api_key", "moderation-test-key")
    provider = build_provider("google")
    assert isinstance(provider, ModeratedProvider)
    assert provider.generation_provider.__class__.__name__ == "GoogleAIProvider"


def test_unknown_provider_is_rejected():
    try:
        build_provider("unknown")
    except ValueError as error:
        assert "not configured or supported" in str(error)
    else:
        raise AssertionError("Unknown providers must be rejected")

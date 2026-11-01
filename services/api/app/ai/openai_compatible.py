import httpx
from app.ai.protocol import ChatMessage, GenerationResult, ModerationResult


def parse_moderation_result(data: dict) -> ModerationResult:
    results = data.get("results") or []
    if not results:
        raise RuntimeError("Moderation provider returned no decision")
    result = results[0]
    categories = result.get("categories") or {}
    flagged_categories = tuple(sorted(key for key, value in categories.items() if value is True))
    return ModerationResult(flagged=bool(result.get("flagged")), categories=flagged_categories)


class OpenAICompatibleProvider:
    """OpenAI API adapter. Chat and moderation both fail closed on provider errors."""

    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1", timeout: float = 45):
        if not api_key:
            raise ValueError("AI provider API key is not configured")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}"}

    async def generate(
        self, *, model: str, messages: list[ChatMessage], temperature: float = 0.8,
        max_tokens: int = 700,
    ) -> GenerationResult:
        payload = {
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers(),
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
        choices = data.get("choices") or []
        if not choices or not choices[0].get("message", {}).get("content"):
            raise RuntimeError("AI provider returned no usable completion")
        usage = data.get("usage") or {}
        return GenerationResult(
            text=choices[0]["message"]["content"],
            input_tokens=usage.get("prompt_tokens"),
            output_tokens=usage.get("completion_tokens"),
            provider="openai",
            model=data.get("model", model),
        )

    async def moderate(self, text: str) -> ModerationResult:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/moderations",
                headers=self._headers(),
                json={"model": "omni-moderation-latest", "input": text},
            )
            response.raise_for_status()
            data = response.json()
        return parse_moderation_result(data)

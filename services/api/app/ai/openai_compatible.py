import httpx
from app.ai.protocol import ChatMessage, GenerationResult


class OpenAICompatibleProvider:
    """OpenAI Chat Completions adapter. Requires a real API key; never fabricates responses."""

    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1", timeout: float = 45):
        if not api_key:
            raise ValueError("AI provider API key is not configured")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

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
                headers={"Authorization": f"Bearer {self.api_key}"},
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
            provider="openai-compatible",
            model=data.get("model", model),
        )

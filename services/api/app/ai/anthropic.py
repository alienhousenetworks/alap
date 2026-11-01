import httpx
from app.ai.protocol import ChatMessage, GenerationResult


class AnthropicProvider:
    def __init__(self, api_key: str, timeout: float = 45):
        if not api_key:
            raise ValueError("Anthropic API key is not configured")
        self.api_key = api_key
        self.timeout = timeout

    async def generate(
        self, *, model: str, messages: list[ChatMessage], temperature: float = 0.8,
        max_tokens: int = 700,
    ) -> GenerationResult:
        system = "\n".join(item.content for item in messages if item.role == "system")
        turns = [
            {"role": item.role, "content": item.content}
            for item in messages
            if item.role in {"user", "assistant"}
        ]
        if not turns:
            raise ValueError("Anthropic requires at least one user or assistant message")
        payload = {"model": model, "messages": turns, "max_tokens": max_tokens, "temperature": temperature}
        if system:
            payload["system"] = system
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
        blocks = data.get("content") or []
        text = "\n".join(block.get("text", "") for block in blocks if block.get("type") == "text").strip()
        if not text:
            raise RuntimeError("Anthropic returned no usable completion")
        usage = data.get("usage") or {}
        return GenerationResult(
            text=text,
            input_tokens=usage.get("input_tokens"),
            output_tokens=usage.get("output_tokens"),
            provider="anthropic",
            model=data.get("model", model),
        )

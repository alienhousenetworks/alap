import httpx
from app.ai.protocol import ChatMessage, GenerationResult


class GoogleAIProvider:
    def __init__(self, api_key: str, timeout: float = 45):
        if not api_key:
            raise ValueError("Google AI API key is not configured")
        self.api_key = api_key
        self.timeout = timeout

    async def generate(
        self, *, model: str, messages: list[ChatMessage], temperature: float = 0.8,
        max_tokens: int = 700,
    ) -> GenerationResult:
        system = "\n".join(item.content for item in messages if item.role == "system")
        turns = [
            {
                "role": "model" if item.role == "assistant" else "user",
                "parts": [{"text": item.content}],
            }
            for item in messages
            if item.role in {"user", "assistant"}
        ]
        if not turns:
            raise ValueError("Google AI requires at least one user or assistant message")
        payload = {
            "contents": turns,
            "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens},
        }
        if system:
            payload["systemInstruction"] = {"parts": [{"text": system}]}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                headers={"x-goog-api-key": self.api_key, "content-type": "application/json"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
        candidates = data.get("candidates") or []
        parts = candidates[0].get("content", {}).get("parts", []) if candidates else []
        text = "\n".join(part.get("text", "") for part in parts if part.get("text")).strip()
        if not text:
            raise RuntimeError("Google AI returned no usable completion")
        usage = data.get("usageMetadata") or {}
        return GenerationResult(
            text=text,
            input_tokens=usage.get("promptTokenCount"),
            output_tokens=usage.get("candidatesTokenCount"),
            provider="google",
            model=model,
        )

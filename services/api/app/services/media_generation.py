import base64
import httpx
from app.ai.openai_compatible import parse_moderation_result
from app.core.config import settings


def _headers():
    if not settings.openai_api_key:
        raise RuntimeError("OpenAI media provider is not configured")
    return {"Authorization": f"Bearer {settings.openai_api_key}"}


async def moderate_text(text: str):
    async with httpx.AsyncClient(timeout=45) as client:
        response = await client.post(
            "https://api.openai.com/v1/moderations",
            headers=_headers(),
            json={"model": "omni-moderation-latest", "input": text},
        )
        response.raise_for_status()
        return parse_moderation_result(response.json())


async def generate_image(prompt: str) -> bytes:
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            "https://api.openai.com/v1/images/generations",
            headers=_headers(),
            json={
                "model": settings.media_image_model,
                "prompt": prompt,
                "size": "1024x1024",
                "quality": "medium",
                "n": 1,
            },
        )
        response.raise_for_status()
        payload = response.json()
    encoded = (payload.get("data") or [{}])[0].get("b64_json")
    if not encoded:
        raise RuntimeError("Image provider returned no image bytes")
    return base64.b64decode(encoded, validate=True)


async def moderate_image(image_bytes: bytes):
    encoded = base64.b64encode(image_bytes).decode("ascii")
    image_data_url = "data:image/png;base64," + encoded
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            "https://api.openai.com/v1/moderations",
            headers=_headers(),
            json={
                "model": "omni-moderation-latest",
                "input": [{"type": "image_url", "image_url": {"url": image_data_url}}],
            },
        )
        response.raise_for_status()
        return parse_moderation_result(response.json())


async def generate_speech(text: str, voice: str) -> bytes:
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            "https://api.openai.com/v1/audio/speech",
            headers=_headers(),
            json={
                "model": settings.media_tts_model,
                "voice": voice,
                "input": text,
                "response_format": "mp3",
            },
        )
        response.raise_for_status()
        if not response.content:
            raise RuntimeError("Speech provider returned an empty audio file")
        return response.content

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class ImageGenerationRequest(BaseModel):
    prompt: str = Field(min_length=5, max_length=1200)


class SpeechGenerationRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4000)
    voice: str = Field(default="alloy", pattern="^(alloy|ash|coral|echo|fable|onyx|nova|sage|shimmer|verse)$")


class MediaAssetResponse(BaseModel):
    id: UUID
    media_type: str
    mime_type: str
    byte_size: int
    created_at: datetime


class MediaUrlResponse(BaseModel):
    url: str
    expires_in: int

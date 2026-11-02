from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class MemoryPreferenceUpdate(BaseModel):
    enabled: bool


class MemoryResponse(BaseModel):
    id: UUID
    category: str
    content: str
    importance: int
    created_at: datetime
    updated_at: datetime


class MemoryCreate(BaseModel):
    category: str = Field(default="preference", pattern="^(preference|identity|relationship|goal|context|boundary)$")
    content: str = Field(min_length=4, max_length=240)
    importance: int = Field(default=3, ge=1, le=5)

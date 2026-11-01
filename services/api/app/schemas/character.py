from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class CharacterCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    description: str = Field(default="", max_length=500)
    personality: dict[str, str] = Field(default_factory=dict)
    greeting: str = Field(default="", max_length=2000)
    visibility: Literal["private", "public"] = "private"

class CharacterUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=80)
    description: str | None = Field(default=None, max_length=500)
    personality: dict[str, str] | None = None
    greeting: str | None = Field(default=None, max_length=2000)
    visibility: Literal["private", "public"] | None = None

class CharacterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    owner_id: UUID | None
    name: str
    description: str
    personality: dict[str, str]
    greeting: str
    visibility: str
    is_published: bool

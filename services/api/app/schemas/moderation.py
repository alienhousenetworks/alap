from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class ModerationDecision(BaseModel):
    reason: str = Field(default="", max_length=1000)


class ModerationAuditResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    actor_user_id: UUID | None
    character_id: UUID | None
    action: str
    reason: str | None
    created_at: datetime

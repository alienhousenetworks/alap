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


class CharacterReportCreate(BaseModel):
    reason: str = Field(pattern="^(spam|sexual_content|minor_safety|violence|harassment|impersonation|other)$")
    details: str = Field(default="", max_length=2000)


class CharacterReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    reporter_user_id: UUID
    character_id: UUID
    reason: str
    details: str | None
    status: str
    resolution_note: str | None
    reviewed_by: UUID | None
    reviewed_at: datetime | None
    created_at: datetime


class ReportResolution(BaseModel):
    status: str = Field(pattern="^(resolved|dismissed)$")
    note: str = Field(default="", max_length=1000)

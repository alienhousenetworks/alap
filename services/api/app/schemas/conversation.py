from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class ConversationCreate(BaseModel):
    character_id: UUID

class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=4000)

class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    user_id: UUID
    character_id: UUID
    title: str
    created_at: datetime
    updated_at: datetime

class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    role: str
    content: str
    provider: str | None
    model: str | None
    input_tokens: int | None
    output_tokens: int | None
    created_at: datetime

class ChatTurnResponse(BaseModel):
    conversation: ConversationResponse
    user_message: MessageResponse
    assistant_message: MessageResponse

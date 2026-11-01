from pydantic import BaseModel, Field

class ModerationDecision(BaseModel):
    reason: str = Field(default="", max_length=1000)

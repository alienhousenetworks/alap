from typing import Annotated
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints
Password = Annotated[str, StringConstraints(min_length=12, max_length=128)]
class RegisterRequest(BaseModel):
    email: EmailStr
    password: Password
    display_name: Annotated[str, Field(min_length=1, max_length=80)]
    confirm_adult: bool
class LoginRequest(BaseModel):
    email: EmailStr
    password: Annotated[str, Field(min_length=1, max_length=128)]
class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=20, max_length=4096)
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: EmailStr
    display_name: str
    is_adult_confirmed: bool

class DeleteAccountRequest(BaseModel):
    password: Annotated[str, Field(min_length=1, max_length=128)]

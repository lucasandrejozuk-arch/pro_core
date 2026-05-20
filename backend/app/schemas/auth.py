from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.app.models.enums import UserRole


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1, max_length=255)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class TokenUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    sector_id: uuid.UUID | None
    sector_name: str | None = None
    full_name: str
    email: str
    role: UserRole
    must_change_password: bool
    permissions: list[str] = []


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    must_change_password: bool
    user: TokenUser


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=255)
    new_password: str = Field(min_length=8, max_length=255)


class UserProfileResponse(TokenUser):
    is_active: bool

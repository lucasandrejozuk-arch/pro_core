from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.app.models.enums import UserRole


class PasswordResetRequestCreate(BaseModel):
    email: str = Field(min_length=3, max_length=255)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class PasswordResetRequestPublicResponse(BaseModel):
    message: str


class PasswordResetResolveRequest(BaseModel):
    new_password: str = Field(min_length=6, max_length=6)

    @field_validator("new_password")
    @classmethod
    def validate_temporary_password(cls, value: str) -> str:
        if not value.isalnum():
            raise ValueError("Temporary password must contain only letters and numbers.")
        if not any(character.islower() for character in value):
            raise ValueError("Temporary password must contain at least one lowercase letter.")
        if not any(character.isupper() for character in value):
            raise ValueError("Temporary password must contain at least one uppercase letter.")
        if not any(character.isdigit() for character in value):
            raise ValueError("Temporary password must contain at least one number.")
        return value


class PasswordResetRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    requester_user_id: uuid.UUID
    requester_email: str
    requester_full_name: str
    requester_role: UserRole
    recipient_role: UserRole
    recipient_sector_id: uuid.UUID | None
    status: str
    resolved_by_user_id: uuid.UUID | None
    resolved_at: datetime | None
    created_at: datetime
    updated_at: datetime

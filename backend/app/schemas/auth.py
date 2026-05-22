from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

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
    resource_access: list[str] = []


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


BackendRestartReasonType = Literal["maintenance", "hang", "other"]


class BackendRestartAuthorizationRequest(BaseModel):
    operator_email: str = Field(min_length=3, max_length=255)
    admin_email: str = Field(min_length=3, max_length=255)
    admin_password: str = Field(min_length=1, max_length=255)
    reason_type: BackendRestartReasonType
    custom_reason: str | None = Field(default=None, max_length=500)

    @field_validator("operator_email", "admin_email")
    @classmethod
    def normalize_restart_email(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("custom_reason")
    @classmethod
    def strip_custom_reason(cls, value: str | None) -> str | None:
        return value.strip() if value else value


class BackendRestartAuthorizationResponse(BaseModel):
    message: str
    notice_id: str
    reason: str
    created_at: datetime


class BackendRestartNoticeResponse(BaseModel):
    id: str
    created_at: datetime
    operator_email: str
    authorized_by_admin_email: str
    reason_type: BackendRestartReasonType
    reason: str


class BackendRestartNoticePollResponse(BaseModel):
    has_notice: bool
    notice: BackendRestartNoticeResponse | None = None


class BackendRestartPermissionsResponse(BaseModel):
    allowed_emails: list[str]


class BackendRestartPermissionsUpdateRequest(BaseModel):
    allowed_emails: list[str] = Field(default_factory=list, max_length=100)

    @field_validator("allowed_emails")
    @classmethod
    def normalize_allowed_emails(cls, value: list[str]) -> list[str]:
        unique: list[str] = []
        seen = set()
        for email in value:
            normalized = email.strip().lower()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            unique.append(normalized)
        return unique

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.app.models.enums import UserRole


class UserBase(BaseModel):
    full_name: str = Field(min_length=1, max_length=160)
    email: str = Field(min_length=3, max_length=255)
    role: UserRole
    sector_id: uuid.UUID | None = None

    @field_validator("full_name")
    @classmethod
    def strip_full_name(cls, value: str) -> str:
        return value.strip()

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=160)
    email: str | None = Field(default=None, min_length=3, max_length=255)
    role: UserRole | None = None
    sector_id: uuid.UUID | None = None
    is_active: bool | None = None

    @field_validator("full_name")
    @classmethod
    def strip_full_name(cls, value: str | None) -> str | None:
        return value.strip() if value else value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str | None) -> str | None:
        return value.strip().lower() if value else value


class UserPasswordReset(BaseModel):
    new_password: str = Field(min_length=8, max_length=128)


class UserSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    sector_id: uuid.UUID | None
    sector_name: str | None = None
    full_name: str
    email: str
    role: UserRole
    is_active: bool


class UserResponse(UserSummaryResponse):
    must_change_password: bool
    created_at: datetime
    updated_at: datetime


class UserResourceAccessResponse(BaseModel):
    user_id: uuid.UUID
    full_name: str
    email: str
    role: UserRole
    sector_id: uuid.UUID | None
    sector_name: str | None = None
    allowed_resources: list[str]
    default_resources: list[str]
    allowed_tool_specialties: list[str] = []
    default_tool_specialties: list[str] = []


class UserResourceAccessUpdate(BaseModel):
    allowed_resources: list[str] = Field(default_factory=list, max_length=100)
    allowed_tool_specialties: list[str] | None = Field(default=None, max_length=20)

    @field_validator("allowed_resources")
    @classmethod
    def normalize_allowed_resources(cls, value: list[str]) -> list[str]:
        normalized: list[str] = []
        seen = set()
        for item in value:
            key = str(item or "").strip()
            if not key or key in seen:
                continue
            seen.add(key)
            normalized.append(key)
        return normalized

    @field_validator("allowed_tool_specialties")
    @classmethod
    def normalize_allowed_tool_specialties(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        normalized: list[str] = []
        seen = set()
        for item in value:
            key = str(item or "").strip().lower()
            if not key or key in seen:
                continue
            seen.add(key)
            normalized.append(key)
        return normalized

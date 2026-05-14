from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

ThemeMode = Literal["light", "dark"]


class SystemSettingsResponse(BaseModel):
    company_id: uuid.UUID
    company_name: str
    trade_name: str | None
    document_number: str | None
    email: str | None
    phone: str | None
    theme: ThemeMode
    backup_enabled: bool
    backup_interval_hours: int
    backup_storage_path: str
    backup_last_run_at: datetime | None


class SystemSettingsUpdate(BaseModel):
    company_name: str | None = Field(default=None, min_length=1, max_length=160)
    trade_name: str | None = Field(default=None, max_length=160)
    document_number: str | None = Field(default=None, max_length=32)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=32)
    theme: ThemeMode | None = None
    backup_enabled: bool | None = None
    backup_interval_hours: int | None = Field(default=None, ge=1, le=720)
    backup_storage_path: str | None = Field(default=None, min_length=1, max_length=1000)

    @field_validator("company_name", "trade_name", "document_number", "email", "phone")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        return value.strip() if value else value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str | None) -> str | None:
        return value.strip().lower() if value else value

    @field_validator("backup_storage_path")
    @classmethod
    def strip_storage_path(cls, value: str | None) -> str | None:
        return value.strip() if value else value


class BackupRunResponse(BaseModel):
    file_name: str
    file_path: str
    file_size_bytes: int
    created_at: datetime
    validated: bool

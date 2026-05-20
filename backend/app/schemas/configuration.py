from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

ThemeMode = Literal["light", "dark"]
ColorPalette = Literal["blue", "green"]


class AppearanceSettingsResponse(BaseModel):
    brand_name: str | None
    brand_subtitle: str | None
    color_palette: ColorPalette
    primary_color: str
    theme: ThemeMode


class SystemSettingsResponse(BaseModel):
    company_id: uuid.UUID
    company_name: str
    trade_name: str | None
    document_number: str | None
    email: str | None
    phone: str | None
    brand_name: str | None
    brand_subtitle: str | None
    color_palette: ColorPalette
    primary_color: str
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
    brand_name: str | None = Field(default=None, max_length=80)
    brand_subtitle: str | None = Field(default=None, max_length=160)
    color_palette: ColorPalette | None = None
    primary_color: str | None = Field(default=None, min_length=7, max_length=7)
    theme: ThemeMode | None = None
    backup_enabled: bool | None = None
    backup_interval_hours: int | None = Field(default=None, ge=1, le=720)
    backup_storage_path: str | None = Field(default=None, min_length=1, max_length=1000)

    @field_validator(
        "company_name",
        "trade_name",
        "document_number",
        "email",
        "phone",
        "brand_name",
        "brand_subtitle",
    )
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

    @field_validator("primary_color")
    @classmethod
    def validate_primary_color(cls, value: str | None) -> str | None:
        if value is None:
            return value

        color = value.strip()
        if len(color) != 7 or not color.startswith("#"):
            raise ValueError("primary_color must use #RRGGBB format.")
        if any(character not in "0123456789abcdefABCDEF" for character in color[1:]):
            raise ValueError("primary_color must use #RRGGBB format.")
        return color


class BackupRunResponse(BaseModel):
    file_name: str
    file_path: str
    file_size_bytes: int
    created_at: datetime
    validated: bool

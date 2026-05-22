from __future__ import annotations

import base64
import binascii
import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

ThemeMode = Literal["light", "dark"]
ColorPalette = Literal["blue", "green", "amber", "ruby", "cyan"]
LanguageCode = Literal["pt-BR", "en-US"]
LoginCoverPreset = Literal["original", "circuit_board", "service_bench", "precision_grid", "custom"]
LOGIN_COVER_MAX_BYTES = 2 * 1024 * 1024
LOGIN_COVER_DATA_URL_PREFIXES = (
    "data:image/png;base64,",
    "data:image/jpeg;base64,",
    "data:image/jpg;base64,",
)


class AppearanceSettingsResponse(BaseModel):
    brand_name: str | None
    brand_subtitle: str | None
    color_palette: ColorPalette
    primary_color: str
    theme: ThemeMode
    language: LanguageCode
    login_cover_preset: LoginCoverPreset
    login_cover_image_data_url: str | None


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
    language: LanguageCode
    login_cover_preset: LoginCoverPreset
    login_cover_image_data_url: str | None
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
    language: LanguageCode | None = None
    login_cover_preset: LoginCoverPreset | None = None
    login_cover_image_data_url: str | None = Field(default=None, max_length=2_900_000)
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

    @field_validator("login_cover_image_data_url")
    @classmethod
    def validate_login_cover_image_data_url(cls, value: str | None) -> str | None:
        if value is None:
            return value

        data_url = value.strip()
        if data_url == "":
            return ""
        prefix = next(
            (
                candidate
                for candidate in LOGIN_COVER_DATA_URL_PREFIXES
                if data_url.lower().startswith(candidate)
            ),
            None,
        )
        if prefix is None:
            raise ValueError("login_cover_image_data_url must be a PNG or JPEG data URL.")

        encoded = data_url[len(prefix) :]
        try:
            decoded = base64.b64decode(encoded, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ValueError("login_cover_image_data_url must contain valid base64.") from exc
        if not decoded:
            raise ValueError("login_cover_image_data_url cannot be empty.")
        if len(decoded) > LOGIN_COVER_MAX_BYTES:
            raise ValueError("login cover image must be at most 2 MB.")
        return data_url


class BackupRunResponse(BaseModel):
    file_name: str
    file_path: str
    file_size_bytes: int
    created_at: datetime
    validated: bool

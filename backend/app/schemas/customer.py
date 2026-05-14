from __future__ import annotations

import uuid
from datetime import datetime
import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

PHONE_PATTERN = re.compile(r"^\(\d{2}\) \d{4,5}-\d{4}$")


class CustomerBase(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    email: str = Field(min_length=3, max_length=255)
    phone: str = Field(min_length=14, max_length=15)
    address: str | None = Field(default=None, max_length=500)
    notes: str | None = Field(default=None, max_length=1000)
    is_active: bool = True

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        return value.strip()

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        normalized = value.strip()
        if not PHONE_PATTERN.match(normalized):
            raise ValueError("Phone must use format (DD) 99999-9999.")
        return normalized


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    email: str | None = Field(default=None, min_length=3, max_length=255)
    phone: str | None = Field(default=None, min_length=14, max_length=15)
    address: str | None = Field(default=None, max_length=500)
    notes: str | None = Field(default=None, max_length=1000)
    is_active: bool | None = None

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str | None) -> str | None:
        return value.strip() if value else value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str | None) -> str | None:
        return value.strip().lower() if value else value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is None:
            return value

        normalized = value.strip()
        if not PHONE_PATTERN.match(normalized):
            raise ValueError("Phone must use format (DD) 99999-9999.")
        return normalized


class CustomerResponse(CustomerBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

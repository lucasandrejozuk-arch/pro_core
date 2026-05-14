from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EquipmentBase(BaseModel):
    customer_id: uuid.UUID
    category: str = Field(min_length=1, max_length=80)
    brand: str | None = Field(default=None, max_length=80)
    model: str | None = Field(default=None, max_length=120)
    serial_number: str | None = Field(default=None, max_length=120)
    description: str | None = Field(default=None, max_length=1000)


class EquipmentCreate(EquipmentBase):
    pass


class EquipmentUpdate(BaseModel):
    customer_id: uuid.UUID | None = None
    category: str | None = Field(default=None, min_length=1, max_length=80)
    brand: str | None = Field(default=None, max_length=80)
    model: str | None = Field(default=None, max_length=120)
    serial_number: str | None = Field(default=None, max_length=120)
    description: str | None = Field(default=None, max_length=1000)


class EquipmentResponse(EquipmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


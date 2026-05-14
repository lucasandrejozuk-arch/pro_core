from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class InventoryItemBase(BaseModel):
    sku: str | None = Field(default=None, max_length=80)
    name: str = Field(min_length=1, max_length=160)
    category: str | None = Field(default=None, max_length=80)
    quantity: Decimal = Field(default=Decimal("0"), ge=0)
    minimum_quantity: Decimal = Field(default=Decimal("0"), ge=0)
    unit_cost: Decimal = Field(default=Decimal("0"), ge=0)

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        return value.strip()


class InventoryItemCreate(InventoryItemBase):
    pass


class InventoryItemUpdate(BaseModel):
    sku: str | None = Field(default=None, max_length=80)
    name: str | None = Field(default=None, min_length=1, max_length=160)
    category: str | None = Field(default=None, max_length=80)
    quantity: Decimal | None = Field(default=None, ge=0)
    minimum_quantity: Decimal | None = Field(default=None, ge=0)
    unit_cost: Decimal | None = Field(default=None, ge=0)


class InventoryItemResponse(InventoryItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


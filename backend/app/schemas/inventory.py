from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from backend.app.services.inventory_rules import validate_inventory_category_requirements


class InventoryItemBase(BaseModel):
    sku: str | None = Field(default=None, max_length=80)
    name: str = Field(min_length=1, max_length=160)
    category: str | None = Field(default=None, max_length=80)
    stock_group: str = Field(default="components", max_length=32)
    location: str | None = Field(default=None, max_length=120)
    quantity: Decimal = Field(default=Decimal("0"), ge=0)
    minimum_quantity: Decimal = Field(default=Decimal("0"), ge=0)
    unit_cost: Decimal = Field(default=Decimal("0"), ge=0)
    notes: str | None = Field(default=None, max_length=2000)
    technical_data: dict[str, str] | None = Field(default=None)

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        return value.strip()

    @field_validator("stock_group")
    @classmethod
    def validate_stock_group(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in {"components", "tools", "software"}:
            raise ValueError("stock_group must be one of: components, tools, software")
        return normalized


class InventoryItemCreate(InventoryItemBase):
    @model_validator(mode="after")
    def validate_technical_data_for_category(self) -> InventoryItemCreate:
        validate_inventory_category_requirements(self.category, self.technical_data)
        return self


class InventoryItemUpdate(BaseModel):
    sku: str | None = Field(default=None, max_length=80)
    name: str | None = Field(default=None, min_length=1, max_length=160)
    category: str | None = Field(default=None, max_length=80)
    stock_group: str | None = Field(default=None, max_length=32)
    location: str | None = Field(default=None, max_length=120)
    quantity: Decimal | None = Field(default=None, ge=0)
    minimum_quantity: Decimal | None = Field(default=None, ge=0)
    unit_cost: Decimal | None = Field(default=None, ge=0)
    notes: str | None = Field(default=None, max_length=2000)
    technical_data: dict[str, str] | None = Field(default=None)

    @field_validator("stock_group")
    @classmethod
    def validate_stock_group(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().lower()
        if normalized not in {"components", "tools", "software"}:
            raise ValueError("stock_group must be one of: components, tools, software")
        return normalized

    @model_validator(mode="after")
    def validate_technical_data_for_category(self) -> InventoryItemUpdate:
        if self.category is not None:
            validate_inventory_category_requirements(self.category, self.technical_data)
        return self


class InventoryItemResponse(InventoryItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

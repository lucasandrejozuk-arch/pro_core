from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class EquipmentBoardComponentBase(BaseModel):
    category: str | None = Field(default=None, max_length=120)
    name: str = Field(min_length=1, max_length=160)
    quantity: str | None = Field(default=None, max_length=40)
    part_number: str | None = Field(default=None, max_length=120)
    location: str | None = Field(default=None, max_length=120)
    unit_price: Decimal = Field(default=Decimal("0"), ge=0)
    notes: str | None = Field(default=None, max_length=1000)


class EquipmentBoardComponentCreate(EquipmentBoardComponentBase):
    pass


class EquipmentBoardComponentUpdate(BaseModel):
    category: str | None = Field(default=None, max_length=120)
    name: str | None = Field(default=None, min_length=1, max_length=160)
    quantity: str | None = Field(default=None, max_length=40)
    part_number: str | None = Field(default=None, max_length=120)
    location: str | None = Field(default=None, max_length=120)
    unit_price: Decimal | None = Field(default=None, ge=0)
    notes: str | None = Field(default=None, max_length=1000)


class EquipmentBoardComponentResponse(EquipmentBoardComponentBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    board_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class EquipmentDefectCaseBase(BaseModel):
    board_id: uuid.UUID | None = None
    title: str = Field(min_length=1, max_length=160)
    symptom: str | None = Field(default=None, max_length=2000)
    root_cause: str | None = Field(default=None, max_length=2000)
    solution: str | None = Field(default=None, max_length=2000)
    notes: str | None = Field(default=None, max_length=2000)


class EquipmentDefectCaseCreate(EquipmentDefectCaseBase):
    pass


class EquipmentDefectCaseUpdate(BaseModel):
    board_id: uuid.UUID | None = None
    title: str | None = Field(default=None, min_length=1, max_length=160)
    symptom: str | None = Field(default=None, max_length=2000)
    root_cause: str | None = Field(default=None, max_length=2000)
    solution: str | None = Field(default=None, max_length=2000)
    notes: str | None = Field(default=None, max_length=2000)


class EquipmentDefectCaseResponse(EquipmentDefectCaseBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    equipment_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class EquipmentBoardBase(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    special_number: str | None = Field(default=None, max_length=120)
    serial_number: str | None = Field(default=None, max_length=120)
    model: str | None = Field(default=None, max_length=120)
    revision: str | None = Field(default=None, max_length=80)
    unit_price: Decimal = Field(default=Decimal("0"), ge=0)
    notes: str | None = Field(default=None, max_length=1000)


class EquipmentBoardCreate(EquipmentBoardBase):
    pass


class EquipmentBoardUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    special_number: str | None = Field(default=None, max_length=120)
    serial_number: str | None = Field(default=None, max_length=120)
    model: str | None = Field(default=None, max_length=120)
    revision: str | None = Field(default=None, max_length=80)
    unit_price: Decimal | None = Field(default=None, ge=0)
    notes: str | None = Field(default=None, max_length=1000)


class EquipmentBoardResponse(EquipmentBoardBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    equipment_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    components: list[EquipmentBoardComponentResponse] = []


class EquipmentBase(BaseModel):
    customer_id: uuid.UUID | None = None
    category: str = Field(min_length=1, max_length=80)
    brand: str | None = Field(default=None, max_length=80)
    model: str | None = Field(default=None, max_length=120)
    special_number: str | None = Field(default=None, max_length=120)
    serial_number: str | None = Field(default=None, max_length=120)
    unit_price: Decimal = Field(default=Decimal("0"), ge=0)
    description: str | None = Field(default=None, max_length=1000)


class EquipmentCreate(EquipmentBase):
    pass


class EquipmentUpdate(BaseModel):
    customer_id: uuid.UUID | None = None
    category: str | None = Field(default=None, min_length=1, max_length=80)
    brand: str | None = Field(default=None, max_length=80)
    model: str | None = Field(default=None, max_length=120)
    special_number: str | None = Field(default=None, max_length=120)
    serial_number: str | None = Field(default=None, max_length=120)
    unit_price: Decimal | None = Field(default=None, ge=0)
    description: str | None = Field(default=None, max_length=1000)


class EquipmentResponse(EquipmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    boards: list[EquipmentBoardResponse] = []
    defect_cases: list[EquipmentDefectCaseResponse] = []

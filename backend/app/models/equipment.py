from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.common import ModelBase

if TYPE_CHECKING:
    from backend.app.models.company import Company
    from backend.app.models.customer import Customer
    from backend.app.models.document import DocumentAttachment
    from backend.app.models.service_order import ServiceOrder


class Equipment(ModelBase, Base):
    __tablename__ = "equipment"

    company_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    brand: Mapped[str | None] = mapped_column(String(80), nullable=True)
    model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    special_number: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    serial_number: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    company: Mapped["Company"] = relationship(back_populates="equipment")
    customer: Mapped["Customer"] = relationship(back_populates="equipment")
    service_orders: Mapped[list["ServiceOrder"]] = relationship(back_populates="equipment")
    documents: Mapped[list["DocumentAttachment"]] = relationship(back_populates="equipment")
    boards: Mapped[list["EquipmentBoard"]] = relationship(
        back_populates="equipment",
        cascade="all, delete-orphan",
    )


class EquipmentBoard(ModelBase, Base):
    __tablename__ = "equipment_boards"

    company_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    equipment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("equipment.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    special_number: Mapped[str | None] = mapped_column(String(120), nullable=True)
    serial_number: Mapped[str | None] = mapped_column(String(120), nullable=True)
    model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    revision: Mapped[str | None] = mapped_column(String(80), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    equipment: Mapped["Equipment"] = relationship(back_populates="boards")
    components: Mapped[list["EquipmentBoardComponent"]] = relationship(
        back_populates="board",
        cascade="all, delete-orphan",
    )


class EquipmentBoardComponent(ModelBase, Base):
    __tablename__ = "equipment_board_components"

    company_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    board_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("equipment_boards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category: Mapped[str | None] = mapped_column(String(120), nullable=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    quantity: Mapped[str | None] = mapped_column(String(40), nullable=True)
    part_number: Mapped[str | None] = mapped_column(String(120), nullable=True)
    location: Mapped[str | None] = mapped_column(String(120), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    board: Mapped["EquipmentBoard"] = relationship(back_populates="components")

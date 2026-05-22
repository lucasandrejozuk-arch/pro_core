from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.common import ModelBase
from backend.app.models.enums import DocumentType, enum_values

if TYPE_CHECKING:
    from backend.app.models.customer import Customer
    from backend.app.models.equipment import Equipment
    from backend.app.models.inventory import InventoryItem
    from backend.app.models.service_order import ServiceOrder
    from backend.app.models.user import User


class DocumentAttachment(ModelBase, Base):
    __tablename__ = "document_attachments"

    company_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    service_order_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("service_orders.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    equipment_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("equipment.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    inventory_item_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("inventory_items.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    uploaded_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    document_type: Mapped[DocumentType] = mapped_column(
        Enum(DocumentType, values_callable=enum_values),
        default=DocumentType.OTHER,
        nullable=False,
        index=True,
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    content_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    service_order: Mapped[ServiceOrder | None] = relationship(back_populates="documents")
    customer: Mapped[Customer | None] = relationship(back_populates="documents")
    equipment: Mapped[Equipment | None] = relationship(back_populates="documents")
    inventory_item: Mapped[InventoryItem | None] = relationship(back_populates="documents")
    uploaded_by: Mapped[User | None] = relationship(
        back_populates="uploaded_documents",
        foreign_keys=[uploaded_by_user_id],
    )

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Enum, ForeignKey, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.common import ModelBase
from backend.app.models.enums import UserRole, enum_values


class User(ModelBase, Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("company_id", "email", name="uq_users_company_email"),)

    company_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sector_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("sectors.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    full_name: Mapped[str] = mapped_column(String(160), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, values_callable=enum_values),
        nullable=False,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    must_change_password: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    company: Mapped["Company"] = relationship(back_populates="users")
    sector: Mapped["Sector | None"] = relationship(back_populates="users")
    assigned_service_orders: Mapped[list["ServiceOrder"]] = relationship(
        back_populates="assigned_technician",
        foreign_keys="ServiceOrder.assigned_technician_id",
    )
    uploaded_documents: Mapped[list["DocumentAttachment"]] = relationship(
        back_populates="uploaded_by",
        foreign_keys="DocumentAttachment.uploaded_by_user_id",
    )

    @property
    def sector_name(self) -> str | None:
        return self.sector.name if self.sector else None

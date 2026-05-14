from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base
from backend.app.models.common import ModelBase
from backend.app.models.enums import UserRole, enum_values


class PasswordResetRequest(ModelBase, Base):
    __tablename__ = "password_reset_requests"

    company_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    requester_user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    requester_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    requester_full_name: Mapped[str] = mapped_column(String(160), nullable=False)
    requester_role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, values_callable=enum_values),
        nullable=False,
        index=True,
    )
    recipient_role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, values_callable=enum_values),
        nullable=False,
        index=True,
    )
    recipient_sector_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("sectors.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False, index=True)
    resolved_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

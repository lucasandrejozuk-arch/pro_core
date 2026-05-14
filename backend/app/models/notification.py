from __future__ import annotations

import uuid

from sqlalchemy import Enum, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.common import ModelBase
from backend.app.models.enums import NotificationChannel, NotificationStatus, enum_values


class NotificationLog(ModelBase, Base):
    __tablename__ = "notification_logs"

    company_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    service_order_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("service_orders.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    channel: Mapped[NotificationChannel] = mapped_column(
        Enum(NotificationChannel, values_callable=enum_values),
        default=NotificationChannel.EMAIL,
        nullable=False,
        index=True,
    )
    status: Mapped[NotificationStatus] = mapped_column(
        Enum(NotificationStatus, values_callable=enum_values),
        default=NotificationStatus.PENDING,
        nullable=False,
        index=True,
    )
    recipient: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[str | None] = mapped_column(String(240), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    provider_response: Mapped[str | None] = mapped_column(Text, nullable=True)

    service_order: Mapped["ServiceOrder | None"] = relationship()

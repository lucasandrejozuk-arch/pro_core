from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.common import ModelBase


class AppSetting(ModelBase, Base):
    __tablename__ = "app_settings"
    __table_args__ = (UniqueConstraint("company_id", "key", name="uq_app_settings_company_key"),)

    company_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    key: Mapped[str] = mapped_column(String(120), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    company: Mapped["Company"] = relationship(back_populates="settings")


class BackupPolicy(ModelBase, Base):
    __tablename__ = "backup_policies"

    company_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    interval_hours: Mapped[int] = mapped_column(Integer, default=24, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1000), default="backups", nullable=False)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    company: Mapped["Company"] = relationship(back_populates="backup_policies")


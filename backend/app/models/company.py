from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.common import ModelBase

if TYPE_CHECKING:
    from backend.app.models.configuration import AppSetting, BackupPolicy
    from backend.app.models.customer import Customer
    from backend.app.models.equipment import Equipment
    from backend.app.models.inventory import InventoryItem
    from backend.app.models.sector import Sector
    from backend.app.models.service_order import ServiceOrder
    from backend.app.models.user import User


class Company(ModelBase, Base):
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(String(160), nullable=False)
    trade_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    document_number: Mapped[str | None] = mapped_column(String(32), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    backup_interval_hours: Mapped[int] = mapped_column(Integer, default=24, nullable=False)

    sectors: Mapped[list[Sector]] = relationship(back_populates="company")
    users: Mapped[list[User]] = relationship(back_populates="company")
    customers: Mapped[list[Customer]] = relationship(back_populates="company")
    equipment: Mapped[list[Equipment]] = relationship(back_populates="company")
    inventory_items: Mapped[list[InventoryItem]] = relationship(back_populates="company")
    service_orders: Mapped[list[ServiceOrder]] = relationship(back_populates="company")
    settings: Mapped[list[AppSetting]] = relationship(back_populates="company")
    backup_policies: Mapped[list[BackupPolicy]] = relationship(back_populates="company")

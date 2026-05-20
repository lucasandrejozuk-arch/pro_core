from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.common import ModelBase

if TYPE_CHECKING:
    from backend.app.models.company import Company
    from backend.app.models.user import User


class Sector(ModelBase, Base):
    __tablename__ = "sectors"
    __table_args__ = (UniqueConstraint("company_id", "name", name="uq_sectors_company_name"),)

    company_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    company: Mapped[Company] = relationship(back_populates="sectors")
    users: Mapped[list[User]] = relationship(back_populates="sector")

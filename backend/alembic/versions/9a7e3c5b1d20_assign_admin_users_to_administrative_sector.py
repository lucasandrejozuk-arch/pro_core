"""assign admin users to administrative sector

Revision ID: 9a7e3c5b1d20
Revises: 2d9f0c8b7a61
Create Date: 2026-05-20 00:00:00.000000
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "9a7e3c5b1d20"
down_revision: str | None = "2d9f0c8b7a61"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ADMIN_SECTOR_NAME = "Administrativo"
ADMIN_SECTOR_DESCRIPTION = "Setor administrativo padrao do sistema."
USER_ROLE_TYPE = sa.Enum("admin", "manager", "technician", "customer", name="userrole")


def upgrade() -> None:
    bind = op.get_bind()
    companies = sa.table("companies", sa.column("id", sa.Uuid()))
    sectors = sa.table(
        "sectors",
        sa.column("id", sa.Uuid()),
        sa.column("company_id", sa.Uuid()),
        sa.column("name", sa.String()),
        sa.column("description", sa.String()),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )
    users = sa.table(
        "users",
        sa.column("company_id", sa.Uuid()),
        sa.column("sector_id", sa.Uuid()),
        sa.column("role", USER_ROLE_TYPE),
    )

    now = sa.func.now()
    for company_id in bind.execute(sa.select(companies.c.id)).scalars():
        sector_id = bind.execute(
            sa.select(sectors.c.id).where(
                sectors.c.company_id == company_id,
                sa.func.lower(sectors.c.name) == ADMIN_SECTOR_NAME.casefold(),
            )
        ).scalar_one_or_none()

        if sector_id is None:
            sector_id = uuid.uuid4()
            bind.execute(
                sectors.insert().values(
                    id=sector_id,
                    company_id=company_id,
                    name=ADMIN_SECTOR_NAME,
                    description=ADMIN_SECTOR_DESCRIPTION,
                    created_at=now,
                    updated_at=now,
                )
            )

        bind.execute(
            users.update()
            .where(
                users.c.company_id == company_id,
                users.c.role == "admin",
                users.c.sector_id.is_(None),
            )
            .values(sector_id=sector_id)
        )


def downgrade() -> None:
    # Data migration only: keep the sector and assignments to avoid losing user scope.
    pass

"""add password reset requests

Revision ID: f3d8a2c5e9b1
Revises: 7c217fbfdc97
Create Date: 2026-05-14 00:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "f3d8a2c5e9b1"
down_revision: str | None = "7c217fbfdc97"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    user_role = postgresql.ENUM(
        "admin",
        "manager",
        "technician",
        "customer",
        name="userrole",
        create_type=False,
    )
    op.create_table(
        "password_reset_requests",
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column("requester_user_id", sa.Uuid(), nullable=False),
        sa.Column("requester_email", sa.String(length=255), nullable=False),
        sa.Column("requester_full_name", sa.String(length=160), nullable=False),
        sa.Column("requester_role", user_role, nullable=False),
        sa.Column("recipient_role", user_role, nullable=False),
        sa.Column("recipient_sector_id", sa.Uuid(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("resolved_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["requester_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["recipient_sector_id"], ["sectors.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["resolved_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_password_reset_requests_company_id"),
        "password_reset_requests",
        ["company_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_password_reset_requests_recipient_role"),
        "password_reset_requests",
        ["recipient_role"],
        unique=False,
    )
    op.create_index(
        op.f("ix_password_reset_requests_recipient_sector_id"),
        "password_reset_requests",
        ["recipient_sector_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_password_reset_requests_requester_email"),
        "password_reset_requests",
        ["requester_email"],
        unique=False,
    )
    op.create_index(
        op.f("ix_password_reset_requests_requester_role"),
        "password_reset_requests",
        ["requester_role"],
        unique=False,
    )
    op.create_index(
        op.f("ix_password_reset_requests_requester_user_id"),
        "password_reset_requests",
        ["requester_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_password_reset_requests_resolved_by_user_id"),
        "password_reset_requests",
        ["resolved_by_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_password_reset_requests_status"),
        "password_reset_requests",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_password_reset_requests_status"),
        table_name="password_reset_requests",
    )
    op.drop_index(
        op.f("ix_password_reset_requests_resolved_by_user_id"),
        table_name="password_reset_requests",
    )
    op.drop_index(
        op.f("ix_password_reset_requests_requester_user_id"),
        table_name="password_reset_requests",
    )
    op.drop_index(
        op.f("ix_password_reset_requests_requester_role"),
        table_name="password_reset_requests",
    )
    op.drop_index(
        op.f("ix_password_reset_requests_requester_email"),
        table_name="password_reset_requests",
    )
    op.drop_index(
        op.f("ix_password_reset_requests_recipient_sector_id"),
        table_name="password_reset_requests",
    )
    op.drop_index(
        op.f("ix_password_reset_requests_recipient_role"),
        table_name="password_reset_requests",
    )
    op.drop_index(
        op.f("ix_password_reset_requests_company_id"),
        table_name="password_reset_requests",
    )
    op.drop_table("password_reset_requests")

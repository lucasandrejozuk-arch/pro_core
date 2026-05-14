from __future__ import annotations

import json
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.audit import AuditLog


def create_audit_log(
    db: Session,
    company_id: uuid.UUID,
    action: str,
    entity_type: str,
    summary: str,
    actor_user_id: uuid.UUID | None = None,
    actor_type: str = "staff",
    entity_id: uuid.UUID | str | None = None,
    metadata: dict[str, Any] | None = None,
    ip_address: str | None = None,
) -> AuditLog:
    audit_log = AuditLog(
        company_id=company_id,
        actor_user_id=actor_user_id,
        actor_type=actor_type,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id is not None else None,
        summary=summary,
        metadata_json=json.dumps(metadata, default=str) if metadata else None,
        ip_address=ip_address,
    )
    db.add(audit_log)
    return audit_log


def list_audit_logs(
    db: Session,
    company_id: uuid.UUID,
    entity_type: str | None = None,
    entity_id: str | None = None,
) -> list[AuditLog]:
    statement = (
        select(AuditLog)
        .where(AuditLog.company_id == company_id)
        .order_by(AuditLog.created_at.desc())
    )
    if entity_type:
        statement = statement.where(AuditLog.entity_type == entity_type)
    if entity_id:
        statement = statement.where(AuditLog.entity_id == entity_id)
    return list(db.scalars(statement))

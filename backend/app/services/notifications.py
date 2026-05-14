from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.enums import NotificationChannel, NotificationStatus
from backend.app.models.notification import NotificationLog


def queue_notification(
    db: Session,
    company_id: uuid.UUID,
    recipient: str,
    message: str,
    channel: NotificationChannel = NotificationChannel.EMAIL,
    service_order_id: uuid.UUID | None = None,
    subject: str | None = None,
) -> NotificationLog:
    notification = NotificationLog(
        company_id=company_id,
        service_order_id=service_order_id,
        channel=channel,
        status=NotificationStatus.PENDING,
        recipient=recipient,
        subject=subject,
        message=message,
    )
    db.add(notification)
    return notification


def list_notifications(
    db: Session,
    company_id: uuid.UUID,
    service_order_id: uuid.UUID | None = None,
) -> list[NotificationLog]:
    statement = (
        select(NotificationLog)
        .where(NotificationLog.company_id == company_id)
        .order_by(NotificationLog.created_at.desc())
    )
    if service_order_id is not None:
        statement = statement.where(NotificationLog.service_order_id == service_order_id)
    return list(db.scalars(statement))

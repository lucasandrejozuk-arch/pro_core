from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.api.dependencies import require_roles
from backend.app.db.session import get_db
from backend.app.models.enums import UserRole
from backend.app.models.user import User
from backend.app.schemas.notification import NotificationLogResponse
from backend.app.services.notifications import list_notifications

router = APIRouter(prefix="/notifications", tags=["notifications"])
admin_or_manager = require_roles(UserRole.ADMIN, UserRole.MANAGER)


@router.get("", response_model=list[NotificationLogResponse])
def list_notification_records(
    service_order_id: uuid.UUID | None = None,
    current_user: User = Depends(admin_or_manager),
    db: Session = Depends(get_db),
) -> list[NotificationLogResponse]:
    return list_notifications(
        db,
        company_id=current_user.company_id,
        service_order_id=service_order_id,
    )

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from backend.app.models.enums import NotificationChannel, NotificationStatus


class NotificationLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    service_order_id: uuid.UUID | None
    channel: NotificationChannel
    status: NotificationStatus
    recipient: str
    subject: str | None
    message: str
    provider_response: str | None
    created_at: datetime
    updated_at: datetime

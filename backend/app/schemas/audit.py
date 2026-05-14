from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    actor_user_id: uuid.UUID | None
    actor_type: str
    action: str
    entity_type: str
    entity_id: str | None
    summary: str
    metadata_json: str | None
    ip_address: str | None
    created_at: datetime
    updated_at: datetime

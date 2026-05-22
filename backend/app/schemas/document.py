from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from backend.app.models.enums import DocumentType


class DocumentAttachmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    service_order_id: uuid.UUID | None
    customer_id: uuid.UUID | None
    equipment_id: uuid.UUID | None
    inventory_item_id: uuid.UUID | None
    uploaded_by_user_id: uuid.UUID | None
    document_type: DocumentType
    file_name: str
    storage_path: str
    content_type: str | None
    file_size_bytes: int | None
    created_at: datetime
    updated_at: datetime

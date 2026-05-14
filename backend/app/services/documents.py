from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.config import Settings, get_settings
from backend.app.models.document import DocumentAttachment
from backend.app.models.enums import DocumentType
from backend.app.services.customers import get_customer
from backend.app.services.equipment import get_equipment
from backend.app.services.service_orders import get_service_order


def list_documents(
    db: Session,
    company_id: uuid.UUID,
    service_order_id: uuid.UUID | None = None,
    customer_id: uuid.UUID | None = None,
    equipment_id: uuid.UUID | None = None,
) -> list[DocumentAttachment]:
    statement = (
        select(DocumentAttachment)
        .where(DocumentAttachment.company_id == company_id)
        .order_by(DocumentAttachment.created_at.desc())
    )

    if service_order_id is not None:
        statement = statement.where(DocumentAttachment.service_order_id == service_order_id)
    if customer_id is not None:
        statement = statement.where(DocumentAttachment.customer_id == customer_id)
    if equipment_id is not None:
        statement = statement.where(DocumentAttachment.equipment_id == equipment_id)

    return list(db.scalars(statement))


def get_document(
    db: Session,
    company_id: uuid.UUID,
    document_id: uuid.UUID,
) -> DocumentAttachment | None:
    statement = select(DocumentAttachment).where(
        DocumentAttachment.id == document_id,
        DocumentAttachment.company_id == company_id,
    )
    return db.scalars(statement).first()


def create_document(
    db: Session,
    company_id: uuid.UUID,
    uploaded_by_user_id: uuid.UUID,
    upload_file: UploadFile,
    document_type: DocumentType,
    service_order_id: uuid.UUID | None = None,
    customer_id: uuid.UUID | None = None,
    equipment_id: uuid.UUID | None = None,
    settings: Settings | None = None,
) -> DocumentAttachment:
    _validate_targets(db, company_id, service_order_id, customer_id, equipment_id)

    document_id = uuid.uuid4()
    file_name = _safe_file_name(upload_file.filename or "attachment")
    storage_path = Path("uploads") / str(company_id) / f"{document_id}_{file_name}"
    storage_root = _storage_root(settings or get_settings())
    destination = storage_root / storage_path
    destination.parent.mkdir(parents=True, exist_ok=True)

    upload_file.file.seek(0)
    with destination.open("wb") as output_file:
        shutil.copyfileobj(upload_file.file, output_file)

    document = DocumentAttachment(
        id=document_id,
        company_id=company_id,
        service_order_id=service_order_id,
        customer_id=customer_id,
        equipment_id=equipment_id,
        uploaded_by_user_id=uploaded_by_user_id,
        document_type=document_type,
        file_name=file_name,
        storage_path=storage_path.as_posix(),
        content_type=upload_file.content_type,
        file_size_bytes=destination.stat().st_size,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def resolve_document_path(document: DocumentAttachment, settings: Settings | None = None) -> Path:
    storage_path = Path(document.storage_path)
    if storage_path.is_absolute():
        return storage_path
    return _storage_root(settings or get_settings()) / storage_path


def _validate_targets(
    db: Session,
    company_id: uuid.UUID,
    service_order_id: uuid.UUID | None,
    customer_id: uuid.UUID | None,
    equipment_id: uuid.UUID | None,
) -> None:
    if service_order_id is None and customer_id is None and equipment_id is None:
        raise ValueError("At least one document target must be provided.")

    if service_order_id is not None and get_service_order(db, company_id, service_order_id) is None:
        raise ValueError("Service order not found.")

    if customer_id is not None and get_customer(db, company_id, customer_id) is None:
        raise ValueError("Customer not found.")

    if equipment_id is not None and get_equipment(db, company_id, equipment_id) is None:
        raise ValueError("Equipment not found.")


def _safe_file_name(file_name: str) -> str:
    cleaned = Path(file_name).name.strip().replace(" ", "_")
    cleaned = "".join(
        character
        for character in cleaned
        if character.isalnum() or character in {"-", "_", "."}
    )
    return cleaned or "attachment"


def _storage_root(settings: Settings) -> Path:
    root = Path(settings.pro_core_storage_dir).expanduser()
    if root.is_absolute():
        return root
    return Path.cwd() / root

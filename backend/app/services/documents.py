from __future__ import annotations

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
from backend.app.services.inventory import get_inventory_item
from backend.app.services.service_orders import get_service_order


def list_documents(
    db: Session,
    company_id: uuid.UUID,
    service_order_id: uuid.UUID | None = None,
    customer_id: uuid.UUID | None = None,
    equipment_id: uuid.UUID | None = None,
    inventory_item_id: uuid.UUID | None = None,
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
    if inventory_item_id is not None:
        statement = statement.where(DocumentAttachment.inventory_item_id == inventory_item_id)

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
    inventory_item_id: uuid.UUID | None = None,
    settings: Settings | None = None,
) -> DocumentAttachment:
    _validate_targets(
        db,
        company_id,
        service_order_id,
        customer_id,
        equipment_id,
        inventory_item_id,
    )
    runtime_settings = settings or get_settings()

    document_id = uuid.uuid4()
    file_name = _safe_file_name(upload_file.filename or "attachment")
    _validate_document_extension(file_name, runtime_settings)
    storage_path = Path("uploads") / str(company_id) / f"{document_id}_{file_name}"
    storage_root = _storage_root(runtime_settings)
    destination = storage_root / storage_path
    destination.parent.mkdir(parents=True, exist_ok=True)

    try:
        file_size_bytes = _copy_upload_file(upload_file, destination, runtime_settings)
    except Exception:
        destination.unlink(missing_ok=True)
        raise

    document = DocumentAttachment(
        id=document_id,
        company_id=company_id,
        service_order_id=service_order_id,
        customer_id=customer_id,
        equipment_id=equipment_id,
        inventory_item_id=inventory_item_id,
        uploaded_by_user_id=uploaded_by_user_id,
        document_type=document_type,
        file_name=file_name,
        storage_path=storage_path.as_posix(),
        content_type=upload_file.content_type,
        file_size_bytes=file_size_bytes,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def resolve_document_path(document: DocumentAttachment, settings: Settings | None = None) -> Path:
    storage_root = _storage_root(settings or get_settings()).resolve()
    storage_path = Path(document.storage_path)
    if storage_path.is_absolute():
        candidate_path = storage_path.resolve()
    else:
        candidate_path = (storage_root / storage_path).resolve()

    try:
        candidate_path.relative_to(storage_root)
    except ValueError as exc:
        raise ValueError("Document path escapes storage root.") from exc

    return candidate_path


def _validate_targets(
    db: Session,
    company_id: uuid.UUID,
    service_order_id: uuid.UUID | None,
    customer_id: uuid.UUID | None,
    equipment_id: uuid.UUID | None,
    inventory_item_id: uuid.UUID | None,
) -> None:
    if (
        service_order_id is None
        and customer_id is None
        and equipment_id is None
        and inventory_item_id is None
    ):
        raise ValueError("At least one document target must be provided.")

    if service_order_id is not None and get_service_order(db, company_id, service_order_id) is None:
        raise ValueError("Service order not found.")

    if customer_id is not None and get_customer(db, company_id, customer_id) is None:
        raise ValueError("Customer not found.")

    if equipment_id is not None and get_equipment(db, company_id, equipment_id) is None:
        raise ValueError("Equipment not found.")

    if (
        inventory_item_id is not None
        and get_inventory_item(db, company_id, inventory_item_id) is None
    ):
        raise ValueError("Inventory item not found.")


def _safe_file_name(file_name: str) -> str:
    cleaned = Path(file_name).name.strip().replace(" ", "_")
    cleaned = "".join(
        character for character in cleaned if character.isalnum() or character in {"-", "_", "."}
    )
    return cleaned or "attachment"


def _validate_document_extension(file_name: str, settings: Settings) -> None:
    suffix = Path(file_name).suffix.lower()
    allowed_extensions = {
        extension.lower() for extension in settings.pro_core_allowed_document_extensions
    }
    if suffix not in allowed_extensions:
        raise ValueError("Document file type is not allowed.")


def _copy_upload_file(upload_file: UploadFile, destination: Path, settings: Settings) -> int:
    total_bytes = 0
    max_bytes = settings.pro_core_max_upload_bytes
    upload_file.file.seek(0)
    with destination.open("wb") as output_file:
        while chunk := upload_file.file.read(1024 * 1024):
            total_bytes += len(chunk)
            if total_bytes > max_bytes:
                raise ValueError(
                    f"Document exceeds maximum size of {max_bytes // (1024 * 1024)} MB."
                )
            output_file.write(chunk)
    return total_bytes


def _storage_root(settings: Settings) -> Path:
    root = Path(settings.pro_core_storage_dir).expanduser()
    if root.is_absolute():
        return root
    return Path.cwd() / root

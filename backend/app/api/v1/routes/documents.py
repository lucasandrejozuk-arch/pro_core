from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.app.api.dependencies import require_roles
from backend.app.db.session import get_db
from backend.app.models.enums import DocumentType, UserRole
from backend.app.models.user import User
from backend.app.schemas.document import DocumentAttachmentResponse
from backend.app.services.documents import (
    create_document,
    get_document,
    list_documents,
    resolve_document_path,
)

router = APIRouter(prefix="/documents", tags=["documents"])
staff_user = require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.TECHNICIAN)


@router.get("", response_model=list[DocumentAttachmentResponse])
def list_document_records(
    service_order_id: uuid.UUID | None = Query(default=None),
    customer_id: uuid.UUID | None = Query(default=None),
    equipment_id: uuid.UUID | None = Query(default=None),
    current_user: User = Depends(staff_user),
    db: Session = Depends(get_db),
) -> list[DocumentAttachmentResponse]:
    return list_documents(
        db=db,
        company_id=current_user.company_id,
        service_order_id=service_order_id,
        customer_id=customer_id,
        equipment_id=equipment_id,
    )


@router.post("", response_model=DocumentAttachmentResponse, status_code=status.HTTP_201_CREATED)
def upload_document_record(
    file: UploadFile = File(...),
    document_type: DocumentType = Form(DocumentType.OTHER),
    service_order_id: uuid.UUID | None = Form(default=None),
    customer_id: uuid.UUID | None = Form(default=None),
    equipment_id: uuid.UUID | None = Form(default=None),
    current_user: User = Depends(staff_user),
    db: Session = Depends(get_db),
) -> DocumentAttachmentResponse:
    try:
        return create_document(
            db=db,
            company_id=current_user.company_id,
            uploaded_by_user_id=current_user.id,
            upload_file=file,
            document_type=document_type,
            service_order_id=service_order_id,
            customer_id=customer_id,
            equipment_id=equipment_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{document_id}/download")
def download_document_record(
    document_id: uuid.UUID,
    current_user: User = Depends(staff_user),
    db: Session = Depends(get_db),
) -> FileResponse:
    document = get_document(db, current_user.company_id, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    document_path = resolve_document_path(document)
    if not document_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document file not found."
        )

    return FileResponse(
        path=document_path,
        media_type=document.content_type or "application/octet-stream",
        filename=document.file_name,
    )

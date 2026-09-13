from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.current_user import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.document import DocumentCreate, DocumentResponse
from app.schemas.document_workflow import DocumentStatusTransition
from app.services.document import (
    create_document,
    get_document,
    list_documents,
)
from app.services.document_workflow import transition_document_status


router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)


@router.post(
    "",
    response_model=DocumentResponse,
    status_code=201,
)
def create_document_endpoint(
    document_data: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = create_document(
        db=db,
        law_office_id=current_user.law_office_id,
        document_data=document_data,
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction or user not found.",
        )

    db.commit()
    db.refresh(document)

    return document


@router.patch(
    "/{document_id}/status",
    response_model=DocumentResponse,
)
def transition_document_status_endpoint(
    document_id: int,
    transition_data: DocumentStatusTransition,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = transition_document_status(
        db=db,
        document_id=document_id,
        law_office_id=current_user.law_office_id,
        new_status=transition_data.new_status,
    )

    if document is None:
        raise HTTPException(
            status_code=400,
            detail="Document not found or status transition is not allowed.",
        )

    db.commit()
    db.refresh(document)

    return document


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
)
def get_document_endpoint(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = get_document(
        db=db,
        document_id=document_id,
        law_office_id=current_user.law_office_id,
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    return document


@router.get(
    "",
    response_model=list[DocumentResponse],
)
def list_documents_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_documents(
        db=db,
        law_office_id=current_user.law_office_id,
    )

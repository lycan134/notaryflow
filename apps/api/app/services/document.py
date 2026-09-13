from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.document import DocumentCreate


def create_document(
    db: Session,
    law_office_id: int,
    document_data: DocumentCreate,
) -> Document | None:
    transaction = (
        db.query(Transaction)
        .filter(
            Transaction.id == document_data.transaction_id,
            Transaction.law_office_id == law_office_id,
        )
        .first()
    )

    if transaction is None:
        return None

    user = (
        db.query(User)
        .filter(
            User.id == document_data.uploaded_by_user_id,
            User.law_office_id == law_office_id,
        )
        .first()
    )

    if user is None:
        return None

    document = Document(
        law_office_id=law_office_id,
        transaction_id=document_data.transaction_id,
        uploaded_by_user_id=document_data.uploaded_by_user_id,
        filename=document_data.filename,
        document_type=document_data.document_type,
        status="UPLOADED",
        storage_key=document_data.storage_key,
    )

    db.add(document)
    db.flush()
    db.refresh(document)

    return document


def get_document(
    db: Session,
    document_id: int,
    law_office_id: int,
) -> Document | None:
    return (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.law_office_id == law_office_id,
        )
        .first()
    )


def list_documents(
    db: Session,
    law_office_id: int,
) -> list[Document]:
    return (
        db.query(Document)
        .filter(Document.law_office_id == law_office_id)
        .order_by(Document.id)
        .all()
    )

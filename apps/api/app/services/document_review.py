from datetime import datetime

from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_review import DocumentReview
from app.models.user import User
from app.schemas.document_review import DocumentReviewCreate


def create_document_review(
    db: Session,
    law_office_id: int,
    review_data: DocumentReviewCreate,
) -> DocumentReview | None:
    document = (
        db.query(Document)
        .filter(
            Document.id == review_data.document_id,
            Document.law_office_id == law_office_id,
        )
        .first()
    )

    if document is None:
        return None

    reviewer = (
        db.query(User)
        .filter(
            User.id == review_data.reviewed_by_user_id,
            User.law_office_id == law_office_id,
        )
        .first()
    )

    if reviewer is None:
        return None

    review = DocumentReview(
        law_office_id=law_office_id,
        document_id=review_data.document_id,
        reviewed_by_user_id=review_data.reviewed_by_user_id,
        result=review_data.result,
        notes=review_data.notes,
        reviewed_at=datetime.utcnow(),
    )

    db.add(review)
    db.flush()
    db.refresh(review)

    return review


def get_document_review(
    db: Session,
    review_id: int,
    law_office_id: int,
) -> DocumentReview | None:
    return (
        db.query(DocumentReview)
        .filter(
            DocumentReview.id == review_id,
            DocumentReview.law_office_id == law_office_id,
        )
        .first()
    )


def list_document_reviews(
    db: Session,
    law_office_id: int,
) -> list[DocumentReview]:
    return (
        db.query(DocumentReview)
        .filter(DocumentReview.law_office_id == law_office_id)
        .order_by(DocumentReview.id)
        .all()
    )
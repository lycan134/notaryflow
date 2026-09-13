from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.current_user import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.document_review import (
    DocumentReviewCreate,
    DocumentReviewResponse,
)
from app.services.document_review import (
    create_document_review,
    get_document_review,
    list_document_reviews,
)


router = APIRouter(
    prefix="/document-reviews",
    tags=["document reviews"],
)


@router.post(
    "",
    response_model=DocumentReviewResponse,
    status_code=201,
)
def create_document_review_endpoint(
    review_data: DocumentReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    review = create_document_review(
        db=db,
        law_office_id=current_user.law_office_id,
        review_data=review_data,
    )

    if review is None:
        raise HTTPException(
            status_code=404,
            detail="Document or reviewer not found.",
        )

    db.commit()
    db.refresh(review)

    return review


@router.get(
    "/{review_id}",
    response_model=DocumentReviewResponse,
)
def get_document_review_endpoint(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    review = get_document_review(
        db=db,
        review_id=review_id,
        law_office_id=current_user.law_office_id,
    )

    if review is None:
        raise HTTPException(
            status_code=404,
            detail="Document review not found.",
        )

    return review


@router.get(
    "",
    response_model=list[DocumentReviewResponse],
)
def list_document_reviews_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_document_reviews(
        db=db,
        law_office_id=current_user.law_office_id,
    )

from sqlalchemy.orm import Session

from app.models.document import Document


ALLOWED_DOCUMENT_STATUS_TRANSITIONS = {
    "UPLOADED": {"UNDER_REVIEW"},
    "UNDER_REVIEW": {"REVIEWED", "REJECTED"},
    "REJECTED": {"UNDER_REVIEW"},
    "REVIEWED": set(),
}


def validate_document_status_transition(
    current_status: str,
    new_status: str,
) -> bool:
    allowed_statuses = ALLOWED_DOCUMENT_STATUS_TRANSITIONS.get(
        current_status,
        set(),
    )

    return new_status in allowed_statuses


def transition_document_status(
    db: Session,
    document_id: int,
    law_office_id: int,
    new_status: str,
) -> Document | None:
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.law_office_id == law_office_id,
        )
        .first()
    )

    if document is None:
        return None

    if not validate_document_status_transition(
        document.status,
        new_status,
    ):
        return None

    document.status = new_status

    db.flush()
    db.refresh(document)

    return document

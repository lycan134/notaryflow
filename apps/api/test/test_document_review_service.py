from datetime import date, datetime

from app.models.client import Client
from app.models.document import Document
from app.models.document_review import DocumentReview
from app.models.law_office import LawOffice
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.document import DocumentCreate
from app.schemas.document_review import DocumentReviewCreate
from app.services.document import create_document
from app.services.document_review import (
    create_document_review,
    get_document_review,
    list_document_reviews,
)


def test_create_document_review(db):
    office = LawOffice(name="Review Test Office")

    user = User(
        email="review-test@example.com",
        full_name="Review Test User",
        role="STAFF",
    )

    client = Client(
        full_name="Review Test Client",
    )

    transaction = Transaction(
        reference_number="REVIEW-001",
        transaction_type="ACKNOWLEDGMENT",
        status="DRAFT",
        title="Review Test Transaction",
        date_received=date(2026, 9, 13),
    )

    office.users.append(user)
    office.clients.append(client)
    office.transactions.append(transaction)
    client.transactions.append(transaction)

    db.add(office)
    db.flush()

    document = create_document(
        db=db,
        law_office_id=office.id,
        document_data=DocumentCreate(
            transaction_id=transaction.id,
            uploaded_by_user_id=user.id,
            filename="review-test.pdf",
            document_type="VALID_ID",
            storage_key="documents/review-test.pdf",
        ),
    )

    assert document is not None

    review_data = DocumentReviewCreate(
        document_id=document.id,
        reviewed_by_user_id=user.id,
        result="REVIEWED",
        notes="Document reviewed successfully.",
    )

    review = create_document_review(
        db=db,
        law_office_id=office.id,
        review_data=review_data,
    )

    assert review is not None
    assert isinstance(review, DocumentReview)
    assert review.law_office_id == office.id
    assert review.document_id == document.id
    assert review.reviewed_by_user_id == user.id
    assert review.result == "REVIEWED"
    assert review.notes == "Document reviewed successfully."
    assert isinstance(review.reviewed_at, datetime)


def test_create_document_review_rejects_other_tenant_document(db):
    office_a = LawOffice(name="Review Document Tenant A")
    office_b = LawOffice(name="Review Document Tenant B")

    user_a = User(
        email="review-document-a@example.com",
        full_name="Review Tenant A User",
        role="STAFF",
    )

    user_b = User(
        email="review-document-b@example.com",
        full_name="Review Tenant B User",
        role="STAFF",
    )

    client_b = Client(
        full_name="Review Tenant B Client",
    )

    transaction_b = Transaction(
        reference_number="REVIEW-B-001",
        transaction_type="JURAT",
        status="DRAFT",
        title="Review Tenant B Transaction",
        date_received=date(2026, 9, 13),
    )

    office_a.users.append(user_a)

    office_b.users.append(user_b)
    office_b.clients.append(client_b)
    office_b.transactions.append(transaction_b)
    client_b.transactions.append(transaction_b)

    db.add_all([office_a, office_b])
    db.flush()

    document_b = create_document(
        db=db,
        law_office_id=office_b.id,
        document_data=DocumentCreate(
            transaction_id=transaction_b.id,
            uploaded_by_user_id=user_b.id,
            filename="tenant-b.pdf",
            document_type="VALID_ID",
            storage_key="documents/tenant-b.pdf",
        ),
    )

    assert document_b is not None

    review = create_document_review(
        db=db,
        law_office_id=office_a.id,
        review_data=DocumentReviewCreate(
            document_id=document_b.id,
            reviewed_by_user_id=user_a.id,
            result="REVIEWED",
        ),
    )

    assert review is None


def test_create_document_review_rejects_other_tenant_reviewer(db):
    office_a = LawOffice(name="Review User Tenant A")
    office_b = LawOffice(name="Review User Tenant B")

    user_a = User(
        email="review-user-a@example.com",
        full_name="Review User Tenant A",
        role="STAFF",
    )

    user_b = User(
        email="review-user-b@example.com",
        full_name="Review User Tenant B",
        role="STAFF",
    )

    client_a = Client(
        full_name="Review User Tenant A Client",
    )

    transaction_a = Transaction(
        reference_number="REVIEW-A-001",
        transaction_type="ACKNOWLEDGMENT",
        status="DRAFT",
        title="Review User Tenant A Transaction",
        date_received=date(2026, 9, 13),
    )

    office_a.users.append(user_a)
    office_a.clients.append(client_a)
    office_a.transactions.append(transaction_a)
    client_a.transactions.append(transaction_a)

    office_b.users.append(user_b)

    db.add_all([office_a, office_b])
    db.flush()

    document_a = create_document(
        db=db,
        law_office_id=office_a.id,
        document_data=DocumentCreate(
            transaction_id=transaction_a.id,
            uploaded_by_user_id=user_a.id,
            filename="tenant-a.pdf",
            document_type="SOURCE_DOCUMENT",
            storage_key="documents/tenant-a.pdf",
        ),
    )

    assert document_a is not None

    review = create_document_review(
        db=db,
        law_office_id=office_a.id,
        review_data=DocumentReviewCreate(
            document_id=document_a.id,
            reviewed_by_user_id=user_b.id,
            result="REVIEWED",
        ),
    )

    assert review is None


def test_get_document_review_is_tenant_scoped(db):
    office_a = LawOffice(name="Review Get Office A")
    office_b = LawOffice(name="Review Get Office B")

    user_a = User(
        email="review-get-a@example.com",
        full_name="Review Get User A",
        role="STAFF",
    )

    client_a = Client(
        full_name="Review Get Client A",
    )

    transaction_a = Transaction(
        reference_number="REVIEW-GET-001",
        transaction_type="ACKNOWLEDGMENT",
        status="DRAFT",
        title="Review Get Transaction",
        date_received=date(2026, 9, 13),
    )

    office_a.users.append(user_a)
    office_a.clients.append(client_a)
    office_a.transactions.append(transaction_a)
    client_a.transactions.append(transaction_a)

    db.add_all([office_a, office_b])
    db.flush()

    document = create_document(
        db=db,
        law_office_id=office_a.id,
        document_data=DocumentCreate(
            transaction_id=transaction_a.id,
            uploaded_by_user_id=user_a.id,
            filename="review-get.pdf",
            document_type="VALID_ID",
            storage_key="documents/review-get.pdf",
        ),
    )

    assert document is not None

    review = create_document_review(
        db=db,
        law_office_id=office_a.id,
        review_data=DocumentReviewCreate(
            document_id=document.id,
            reviewed_by_user_id=user_a.id,
            result="REVIEWED",
            notes="Tenant-scoped review.",
        ),
    )

    assert review is not None

    result = get_document_review(
        db=db,
        review_id=review.id,
        law_office_id=office_a.id,
    )

    assert result is not None
    assert result.id == review.id

    other_result = get_document_review(
        db=db,
        review_id=review.id,
        law_office_id=office_b.id,
    )

    assert other_result is None


def test_list_document_reviews_is_tenant_scoped(db):
    office_a = LawOffice(name="Review List Office A")
    office_b = LawOffice(name="Review List Office B")

    user_a = User(
        email="review-list-a@example.com",
        full_name="Review List User A",
        role="STAFF",
    )

    user_b = User(
        email="review-list-b@example.com",
        full_name="Review List User B",
        role="STAFF",
    )

    client_a = Client(full_name="Review List Client A")
    client_b = Client(full_name="Review List Client B")

    transaction_a = Transaction(
        reference_number="REVIEW-LIST-A",
        transaction_type="ACKNOWLEDGMENT",
        status="DRAFT",
        title="Office A Review Transaction",
        date_received=date(2026, 9, 13),
    )

    transaction_b = Transaction(
        reference_number="REVIEW-LIST-B",
        transaction_type="JURAT",
        status="DRAFT",
        title="Office B Review Transaction",
        date_received=date(2026, 9, 13),
    )

    office_a.users.append(user_a)
    office_a.clients.append(client_a)
    office_a.transactions.append(transaction_a)
    client_a.transactions.append(transaction_a)

    office_b.users.append(user_b)
    office_b.clients.append(client_b)
    office_b.transactions.append(transaction_b)
    client_b.transactions.append(transaction_b)

    db.add_all([office_a, office_b])
    db.flush()

    document_a = create_document(
        db=db,
        law_office_id=office_a.id,
        document_data=DocumentCreate(
            transaction_id=transaction_a.id,
            uploaded_by_user_id=user_a.id,
            filename="office-a-review.pdf",
            document_type="VALID_ID",
            storage_key="documents/office-a-review.pdf",
        ),
    )

    document_b = create_document(
        db=db,
        law_office_id=office_b.id,
        document_data=DocumentCreate(
            transaction_id=transaction_b.id,
            uploaded_by_user_id=user_b.id,
            filename="office-b-review.pdf",
            document_type="SOURCE_DOCUMENT",
            storage_key="documents/office-b-review.pdf",
        ),
    )

    assert document_a is not None
    assert document_b is not None

    review_a = create_document_review(
        db=db,
        law_office_id=office_a.id,
        review_data=DocumentReviewCreate(
            document_id=document_a.id,
            reviewed_by_user_id=user_a.id,
            result="REVIEWED",
        ),
    )

    review_b = create_document_review(
        db=db,
        law_office_id=office_b.id,
        review_data=DocumentReviewCreate(
            document_id=document_b.id,
            reviewed_by_user_id=user_b.id,
            result="REJECTED",
            notes="Document requires correction.",
        ),
    )

    assert review_a is not None
    assert review_b is not None

    reviews_a = list_document_reviews(
        db=db,
        law_office_id=office_a.id,
    )

    assert len(reviews_a) == 1
    assert reviews_a[0].id == review_a.id

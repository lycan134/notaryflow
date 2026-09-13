from datetime import date, datetime

from fastapi.testclient import TestClient

from app.db.database import SessionLocal
from app.main import app
from app.models.client import Client
from app.models.document import Document
from app.models.document_review import DocumentReview
from app.models.law_office import LawOffice
from app.models.transaction import Transaction
from app.models.user import User


client = TestClient(app)


def test_create_document_review_endpoint():
    db = SessionLocal()

    try:
        user_record = db.get(User, 24)

        assert user_record is not None
        assert user_record.law_office_id == 52

        client_record = Client(
            law_office_id=52,
            full_name="Document Review API Create Client",
        )

        db.add(client_record)
        db.flush()

        transaction_record = Transaction(
            law_office_id=52,
            client_id=client_record.id,
            transaction_type="ACKNOWLEDGMENT",
            status="DRAFT",
            title="Document Review API Test Transaction",
            date_received=date(2026, 9, 13),
        )

        db.add(transaction_record)
        db.flush()

        document_record = Document(
            law_office_id=52,
            transaction_id=transaction_record.id,
            uploaded_by_user_id=user_record.id,
            filename="review-test.pdf",
            document_type="SOURCE_DOCUMENT",
            status="UPLOADED",
            storage_key="documents/review-test.pdf",
        )

        db.add(document_record)
        db.commit()
        db.refresh(document_record)

        response = client.post(
            "/api/v1/document-reviews",
            json={
                "document_id": document_record.id,
                "reviewed_by_user_id": user_record.id,
                "result": "REVIEWED",
                "notes": "Document reviewed successfully.",
            },
        )

        assert response.status_code == 201

        data = response.json()

        assert data["id"] is not None
        assert data["law_office_id"] == 52
        assert data["document_id"] == document_record.id
        assert data["reviewed_by_user_id"] == user_record.id
        assert data["result"] == "REVIEWED"
        assert data["notes"] == "Document reviewed successfully."
        assert data["reviewed_at"] is not None

        review_record = db.get(DocumentReview, data["id"])

    finally:
        if "review_record" in locals() and review_record is not None:
            db.delete(review_record)

        if "document_record" in locals() and document_record.id is not None:
            db.delete(document_record)

        if "transaction_record" in locals() and transaction_record.id is not None:
            db.delete(transaction_record)

        if "client_record" in locals() and client_record.id is not None:
            db.delete(client_record)

        db.commit()
        db.close()


def test_get_document_review_endpoint_is_tenant_scoped():
    db = SessionLocal()

    try:
        user_record = db.get(User, 24)

        assert user_record is not None
        assert user_record.law_office_id == 52

        client_record = Client(
            law_office_id=52,
            full_name="Document Review API GET Client",
        )

        db.add(client_record)
        db.flush()

        transaction_record = Transaction(
            law_office_id=52,
            client_id=client_record.id,
            transaction_type="ACKNOWLEDGMENT",
            status="DRAFT",
            title="Document Review API GET Transaction",
            date_received=date(2026, 9, 13),
        )

        db.add(transaction_record)
        db.flush()

        document_record = Document(
            law_office_id=52,
            transaction_id=transaction_record.id,
            uploaded_by_user_id=user_record.id,
            filename="review-get-test.pdf",
            document_type="SOURCE_DOCUMENT",
            status="UPLOADED",
            storage_key="documents/review-get-test.pdf",
        )

        db.add(document_record)
        db.flush()

        review_record = DocumentReview(
            law_office_id=52,
            document_id=document_record.id,
            reviewed_by_user_id=user_record.id,
            result="REVIEWED",
            notes="GET endpoint test.",
            reviewed_at=datetime.utcnow(),
        )

        db.add(review_record)
        db.commit()
        db.refresh(review_record)

        response = client.get(
            f"/api/v1/document-reviews/{review_record.id}",
        )

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == review_record.id
        assert data["law_office_id"] == 52
        assert data["document_id"] == document_record.id
        assert data["reviewed_by_user_id"] == user_record.id
        assert data["result"] == "REVIEWED"
        assert data["notes"] == "GET endpoint test."

    finally:
        if "review_record" in locals() and review_record.id is not None:
            db.delete(review_record)

        if "document_record" in locals() and document_record.id is not None:
            db.delete(document_record)

        if "transaction_record" in locals() and transaction_record.id is not None:
            db.delete(transaction_record)

        if "client_record" in locals() and client_record.id is not None:
            db.delete(client_record)

        db.commit()
        db.close()


def test_get_document_review_endpoint_returns_404_for_missing_review():
    response = client.get("/api/v1/document-reviews/999999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Document review not found."


def test_list_document_reviews_endpoint():
    db = SessionLocal()

    try:
        user_record = db.get(User, 24)

        assert user_record is not None
        assert user_record.law_office_id == 52

        client_record = Client(
            law_office_id=52,
            full_name="Document Review List API Client",
        )

        db.add(client_record)
        db.flush()

        transaction_record = Transaction(
            law_office_id=52,
            client_id=client_record.id,
            transaction_type="ACKNOWLEDGMENT",
            status="DRAFT",
            title="Document Review List API Transaction",
            date_received=date(2026, 9, 13),
        )

        db.add(transaction_record)
        db.flush()

        document_a = Document(
            law_office_id=52,
            transaction_id=transaction_record.id,
            uploaded_by_user_id=user_record.id,
            filename="review-list-a.pdf",
            document_type="VALID_ID",
            status="UPLOADED",
            storage_key="documents/review-list-a.pdf",
        )

        document_b = Document(
            law_office_id=52,
            transaction_id=transaction_record.id,
            uploaded_by_user_id=user_record.id,
            filename="review-list-b.pdf",
            document_type="SOURCE_DOCUMENT",
            status="UPLOADED",
            storage_key="documents/review-list-b.pdf",
        )

        db.add_all([document_a, document_b])
        db.flush()

        review_a = DocumentReview(
            law_office_id=52,
            document_id=document_a.id,
            reviewed_by_user_id=user_record.id,
            result="REVIEWED",
            notes="Review A.",
            reviewed_at=datetime.utcnow(),
        )

        review_b = DocumentReview(
            law_office_id=52,
            document_id=document_b.id,
            reviewed_by_user_id=user_record.id,
            result="REJECTED",
            notes="Review B.",
            reviewed_at=datetime.utcnow(),
        )

        db.add_all([review_a, review_b])
        db.commit()

        response = client.get("/api/v1/document-reviews")

        assert response.status_code == 200

        data = response.json()

        returned_ids = [item["id"] for item in data]

        assert review_a.id in returned_ids
        assert review_b.id in returned_ids

    finally:
        if "review_a" in locals() and review_a.id is not None:
            db.delete(review_a)

        if "review_b" in locals() and review_b.id is not None:
            db.delete(review_b)

        if "document_a" in locals() and document_a.id is not None:
            db.delete(document_a)

        if "document_b" in locals() and document_b.id is not None:
            db.delete(document_b)

        if "transaction_record" in locals() and transaction_record.id is not None:
            db.delete(transaction_record)

        if "client_record" in locals() and client_record.id is not None:
            db.delete(client_record)

        db.commit()
        db.close()


def test_list_document_reviews_endpoint_excludes_other_tenant():
    db = SessionLocal()

    try:
        user_record = db.get(User, 24)

        assert user_record is not None
        assert user_record.law_office_id == 52

        other_office = LawOffice(
            name="Other Document Review List API Office",
        )

        db.add(other_office)
        db.flush()

        other_user = User(
            law_office_id=other_office.id,
            email="other-document-review-list-api@example.com",
            full_name="Other Document Review List API User",
            role="STAFF",
            is_active=True,
        )

        db.add(other_user)
        db.flush()

        other_client = Client(
            law_office_id=other_office.id,
            full_name="Other Tenant Document Review List Client",
        )

        db.add(other_client)
        db.flush()

        other_transaction = Transaction(
            law_office_id=other_office.id,
            client_id=other_client.id,
            transaction_type="ACKNOWLEDGMENT",
            status="DRAFT",
            title="Other Tenant Document Review List Transaction",
            date_received=date(2026, 9, 13),
        )

        db.add(other_transaction)
        db.flush()

        other_document = Document(
            law_office_id=other_office.id,
            transaction_id=other_transaction.id,
            uploaded_by_user_id=other_user.id,
            filename="other-tenant-review-document.pdf",
            document_type="VALID_ID",
            status="UPLOADED",
            storage_key="documents/other-tenant-review-document.pdf",
        )

        db.add(other_document)
        db.flush()

        other_review = DocumentReview(
            law_office_id=other_office.id,
            document_id=other_document.id,
            reviewed_by_user_id=other_user.id,
            result="REVIEWED",
            notes="Other tenant review.",
            reviewed_at=datetime.utcnow(),
        )

        db.add(other_review)
        db.commit()

        response = client.get("/api/v1/document-reviews")

        assert response.status_code == 200

        data = response.json()

        returned_ids = [item["id"] for item in data]

        assert other_review.id not in returned_ids

    finally:
        if "other_review" in locals() and other_review.id is not None:
            db.delete(other_review)

        if "other_document" in locals() and other_document.id is not None:
            db.delete(other_document)

        if "other_transaction" in locals() and other_transaction.id is not None:
            db.delete(other_transaction)

        if "other_client" in locals() and other_client.id is not None:
            db.delete(other_client)

        if "other_user" in locals() and other_user.id is not None:
            db.delete(other_user)

        if "other_office" in locals() and other_office.id is not None:
            db.delete(other_office)

        db.commit()
        db.close()

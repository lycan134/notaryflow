from datetime import date

from fastapi.testclient import TestClient

from app.db.database import SessionLocal
from app.main import app
from app.models.client import Client
from app.models.document import Document
from app.models.law_office import LawOffice
from app.models.transaction import Transaction
from app.models.user import User


client = TestClient(app)


def create_test_document(db):
    user_record = db.get(User, 24)

    assert user_record is not None
    assert user_record.law_office_id == 52

    client_record = Client(
        law_office_id=52,
        full_name="Workflow API Client",
    )
    db.add(client_record)
    db.flush()

    transaction_record = Transaction(
        law_office_id=52,
        client_id=client_record.id,
        transaction_type="ACKNOWLEDGMENT",
        status="DRAFT",
        title="Workflow API Transaction",
        date_received=date(2026, 9, 13),
    )
    db.add(transaction_record)
    db.flush()

    document_record = Document(
        law_office_id=52,
        transaction_id=transaction_record.id,
        uploaded_by_user_id=user_record.id,
        filename="workflow-api-test.pdf",
        document_type="SOURCE_DOCUMENT",
        status="UPLOADED",
        storage_key="documents/workflow-api-test.pdf",
    )
    db.add(document_record)
    db.commit()
    db.refresh(document_record)

    return client_record, transaction_record, document_record


def test_transition_document_status_endpoint():
    db = SessionLocal()

    try:
        client_record, transaction_record, document_record = create_test_document(db)

        response = client.patch(
            f"/api/v1/documents/{document_record.id}/status",
            json={"new_status": "UNDER_REVIEW"},
        )

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == document_record.id
        assert data["status"] == "UNDER_REVIEW"

    finally:
        if "document_record" in locals() and document_record.id is not None:
            db.delete(document_record)

        if "transaction_record" in locals() and transaction_record.id is not None:
            db.delete(transaction_record)

        if "client_record" in locals() and client_record.id is not None:
            db.delete(client_record)

        db.commit()
        db.close()


def test_transition_document_status_endpoint_allows_valid_workflow():
    db = SessionLocal()

    try:
        client_record, transaction_record, document_record = create_test_document(db)

        transitions = [
            "UNDER_REVIEW",
            "REJECTED",
            "UNDER_REVIEW",
            "REVIEWED",
        ]

        for new_status in transitions:
            response = client.patch(
                f"/api/v1/documents/{document_record.id}/status",
                json={"new_status": new_status},
            )

            assert response.status_code == 200
            assert response.json()["status"] == new_status

    finally:
        if "document_record" in locals() and document_record.id is not None:
            db.delete(document_record)

        if "transaction_record" in locals() and transaction_record.id is not None:
            db.delete(transaction_record)

        if "client_record" in locals() and client_record.id is not None:
            db.delete(client_record)

        db.commit()
        db.close()


def test_transition_document_status_endpoint_rejects_invalid_transition():
    db = SessionLocal()

    try:
        client_record, transaction_record, document_record = create_test_document(db)

        response = client.patch(
            f"/api/v1/documents/{document_record.id}/status",
            json={"new_status": "REVIEWED"},
        )

        assert response.status_code == 400
        assert response.json()["detail"] == (
            "Document not found or status transition is not allowed."
        )

    finally:
        if "document_record" in locals() and document_record.id is not None:
            db.delete(document_record)

        if "transaction_record" in locals() and transaction_record.id is not None:
            db.delete(transaction_record)

        if "client_record" in locals() and client_record.id is not None:
            db.delete(client_record)

        db.commit()
        db.close()


def test_transition_document_status_endpoint_returns_400_for_missing_document():
    response = client.patch(
        "/api/v1/documents/999999999/status",
        json={"new_status": "UNDER_REVIEW"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Document not found or status transition is not allowed."
    )


def test_transition_document_status_endpoint_is_tenant_scoped():
    db = SessionLocal()

    try:
        other_office = LawOffice(
            name="Other Workflow API Office",
        )
        db.add(other_office)
        db.flush()

        other_user = User(
            law_office_id=other_office.id,
            email="other-workflow-api@example.com",
            full_name="Other Workflow API User",
            role="STAFF",
            is_active=True,
        )
        db.add(other_user)
        db.flush()

        other_client = Client(
            law_office_id=other_office.id,
            full_name="Other Workflow API Client",
        )
        db.add(other_client)
        db.flush()

        other_transaction = Transaction(
            law_office_id=other_office.id,
            client_id=other_client.id,
            transaction_type="ACKNOWLEDGMENT",
            status="DRAFT",
            title="Other Workflow API Transaction",
            date_received=date(2026, 9, 13),
        )
        db.add(other_transaction)
        db.flush()

        other_document = Document(
            law_office_id=other_office.id,
            transaction_id=other_transaction.id,
            uploaded_by_user_id=other_user.id,
            filename="other-tenant-workflow-api.pdf",
            document_type="SOURCE_DOCUMENT",
            status="UPLOADED",
            storage_key="documents/other-tenant-workflow-api.pdf",
        )
        db.add(other_document)
        db.commit()
        db.refresh(other_document)

        response = client.patch(
            f"/api/v1/documents/{other_document.id}/status",
            json={"new_status": "UNDER_REVIEW"},
        )

        assert response.status_code == 400
        assert response.json()["detail"] == (
            "Document not found or status transition is not allowed."
        )

        db.refresh(other_document)
        assert other_document.status == "UPLOADED"

    finally:
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

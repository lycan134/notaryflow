from datetime import date

from fastapi.testclient import TestClient

from app.db.database import SessionLocal
from app.main import app
from app.models.client import Client
from app.models.document import Document
from app.models.transaction import Transaction
from app.models.user import User
from app.models.law_office import LawOffice


client = TestClient(app)


def test_create_document_endpoint():
    db = SessionLocal()

    try:
        user_record = db.get(User, 24)

        assert user_record is not None
        assert user_record.law_office_id == 52

        client_record = Client(
            law_office_id=52,
            full_name="Document API Create Client",
        )

        db.add(client_record)
        db.flush()

        transaction_record = Transaction(
            law_office_id=52,
            client_id=client_record.id,
            reference_number="DOC-API-001",
            transaction_type="ACKNOWLEDGMENT",
            status="DRAFT",
            title="Document API Test Transaction",
            date_received=date(2026, 9, 13),
        )

        db.add(transaction_record)
        db.commit()
        db.refresh(transaction_record)

        response = client.post(
            "/api/v1/documents",
            json={
                "transaction_id": transaction_record.id,
                "uploaded_by_user_id": user_record.id,
                "filename": "valid-id.pdf",
                "document_type": "VALID_ID",
                "storage_key": "documents/valid-id.pdf",
            },
        )

        assert response.status_code == 201

        data = response.json()

        assert data["id"] is not None
        assert data["law_office_id"] == 52
        assert data["transaction_id"] == transaction_record.id
        assert data["uploaded_by_user_id"] == user_record.id
        assert data["filename"] == "valid-id.pdf"
        assert data["document_type"] == "VALID_ID"
        assert data["status"] == "UPLOADED"
        assert data["storage_key"] == "documents/valid-id.pdf"

        document_record = db.get(Document, data["id"])

    finally:
        if "document_record" in locals() and document_record is not None:
            db.delete(document_record)

        if "transaction_record" in locals() and transaction_record.id is not None:
            db.delete(transaction_record)

        if "client_record" in locals() and client_record.id is not None:
            db.delete(client_record)

        db.commit()
        db.close()


def test_get_document_endpoint_is_tenant_scoped():
    db = SessionLocal()

    try:
        user_record = db.get(User, 24)

        assert user_record is not None
        assert user_record.law_office_id == 52

        client_record = Client(
            law_office_id=52,
            full_name="Document API GET Client",
        )

        db.add(client_record)
        db.flush()

        transaction_record = Transaction(
            law_office_id=52,
            client_id=client_record.id,
            reference_number="DOC-GET-API-001",
            transaction_type="ACKNOWLEDGMENT",
            status="DRAFT",
            title="Document API GET Transaction",
            date_received=date(2026, 9, 13),
        )

        db.add(transaction_record)
        db.flush()

        document_record = Document(
            law_office_id=52,
            transaction_id=transaction_record.id,
            uploaded_by_user_id=user_record.id,
            filename="get-test.pdf",
            document_type="SOURCE_DOCUMENT",
            status="UPLOADED",
            storage_key="documents/get-test.pdf",
        )

        db.add(document_record)
        db.commit()
        db.refresh(document_record)

        response = client.get(
            f"/api/v1/documents/{document_record.id}",
        )

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == document_record.id
        assert data["law_office_id"] == 52
        assert data["transaction_id"] == transaction_record.id
        assert data["uploaded_by_user_id"] == user_record.id
        assert data["filename"] == "get-test.pdf"
        assert data["document_type"] == "SOURCE_DOCUMENT"
        assert data["status"] == "UPLOADED"
        assert data["storage_key"] == "documents/get-test.pdf"

    finally:
        if "document_record" in locals() and document_record.id is not None:
            db.delete(document_record)

        if "transaction_record" in locals() and transaction_record.id is not None:
            db.delete(transaction_record)

        if "client_record" in locals() and client_record.id is not None:
            db.delete(client_record)

        db.commit()
        db.close()


def test_get_document_endpoint_returns_404_for_missing_document():
    response = client.get("/api/v1/documents/999999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found."


def test_list_documents_endpoint():
    db = SessionLocal()

    try:
        user_record = db.get(User, 24)

        assert user_record is not None
        assert user_record.law_office_id == 52

        client_record = Client(
            law_office_id=52,
            full_name="Document List API Client",
        )

        db.add(client_record)
        db.flush()

        transaction_record = Transaction(
            law_office_id=52,
            client_id=client_record.id,
            transaction_type="ACKNOWLEDGMENT",
            status="DRAFT",
            title="Document List API Transaction",
            date_received=date(2026, 9, 13),
        )

        db.add(transaction_record)
        db.flush()

        document_a = Document(
            law_office_id=52,
            transaction_id=transaction_record.id,
            uploaded_by_user_id=user_record.id,
            filename="list-document-a.pdf",
            document_type="VALID_ID",
            status="UPLOADED",
            storage_key="documents/list-document-a.pdf",
        )

        document_b = Document(
            law_office_id=52,
            transaction_id=transaction_record.id,
            uploaded_by_user_id=user_record.id,
            filename="list-document-b.pdf",
            document_type="SOURCE_DOCUMENT",
            status="UPLOADED",
            storage_key="documents/list-document-b.pdf",
        )

        db.add_all([document_a, document_b])
        db.commit()

        response = client.get("/api/v1/documents")

        assert response.status_code == 200

        data = response.json()

        returned_filenames = [item["filename"] for item in data]

        assert "list-document-a.pdf" in returned_filenames
        assert "list-document-b.pdf" in returned_filenames

    finally:
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


def test_list_documents_endpoint_excludes_other_tenant():
    db = SessionLocal()

    try:
        user_record = db.get(User, 24)

        assert user_record is not None
        assert user_record.law_office_id == 52

        other_office = LawOffice(
            name="Other Document List API Office",
        )

        db.add(other_office)
        db.flush()

        other_user = User(
            law_office_id=other_office.id,
            email="other-document-list-api@example.com",
            full_name="Other Document List API User",
            role="STAFF",
            is_active=True,
        )

        db.add(other_user)
        db.flush()

        other_client = Client(
            law_office_id=other_office.id,
            full_name="Other Tenant Document List Client",
        )

        db.add(other_client)
        db.flush()

        other_transaction = Transaction(
            law_office_id=other_office.id,
            client_id=other_client.id,
            transaction_type="ACKNOWLEDGMENT",
            status="DRAFT",
            title="Other Tenant Document List Transaction",
            date_received=date(2026, 9, 13),
        )

        db.add(other_transaction)
        db.flush()

        other_document = Document(
            law_office_id=other_office.id,
            transaction_id=other_transaction.id,
            uploaded_by_user_id=other_user.id,
            filename="other-tenant-document.pdf",
            document_type="VALID_ID",
            status="UPLOADED",
            storage_key="documents/other-tenant-document.pdf",
        )

        db.add(other_document)
        db.commit()

        response = client.get("/api/v1/documents")

        assert response.status_code == 200

        data = response.json()

        returned_filenames = [item["filename"] for item in data]

        assert "other-tenant-document.pdf" not in returned_filenames

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

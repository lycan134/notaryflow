from datetime import date

from app.db.database import SessionLocal
from app.models.client import Client
from app.models.document import Document
from app.models.law_office import LawOffice
from app.models.transaction import Transaction
from app.models.user import User
from app.services.document_workflow import transition_document_status


def test_transition_document_status():
    db = SessionLocal()

    try:
        user_record = db.get(User, 24)

        assert user_record is not None
        assert user_record.law_office_id == 52

        client_record = Client(
            law_office_id=52,
            full_name="Workflow Service Client",
        )

        db.add(client_record)
        db.flush()

        transaction_record = Transaction(
            law_office_id=52,
            client_id=client_record.id,
            transaction_type="ACKNOWLEDGMENT",
            status="DRAFT",
            title="Workflow Service Transaction",
            date_received=date(2026, 9, 13),
        )

        db.add(transaction_record)
        db.flush()

        document_record = Document(
            law_office_id=52,
            transaction_id=transaction_record.id,
            uploaded_by_user_id=user_record.id,
            filename="workflow-test.pdf",
            document_type="SOURCE_DOCUMENT",
            status="UPLOADED",
            storage_key="documents/workflow-test.pdf",
        )

        db.add(document_record)
        db.commit()
        db.refresh(document_record)

        result = transition_document_status(
            db=db,
            document_id=document_record.id,
            law_office_id=52,
            new_status="UNDER_REVIEW",
        )

        assert result is not None
        assert result.status == "UNDER_REVIEW"

    finally:
        if "document_record" in locals() and document_record.id is not None:
            db.delete(document_record)

        if "transaction_record" in locals() and transaction_record.id is not None:
            db.delete(transaction_record)

        if "client_record" in locals() and client_record.id is not None:
            db.delete(client_record)

        db.commit()
        db.close()


def test_transition_document_status_rejects_invalid_transition():
    db = SessionLocal()

    try:
        user_record = db.get(User, 24)

        assert user_record is not None
        assert user_record.law_office_id == 52

        client_record = Client(
            law_office_id=52,
            full_name="Invalid Workflow Client",
        )

        db.add(client_record)
        db.flush()

        transaction_record = Transaction(
            law_office_id=52,
            client_id=client_record.id,
            transaction_type="ACKNOWLEDGMENT",
            status="DRAFT",
            title="Invalid Workflow Transaction",
            date_received=date(2026, 9, 13),
        )

        db.add(transaction_record)
        db.flush()

        document_record = Document(
            law_office_id=52,
            transaction_id=transaction_record.id,
            uploaded_by_user_id=user_record.id,
            filename="invalid-workflow-test.pdf",
            document_type="SOURCE_DOCUMENT",
            status="UPLOADED",
            storage_key="documents/invalid-workflow-test.pdf",
        )

        db.add(document_record)
        db.commit()
        db.refresh(document_record)

        result = transition_document_status(
            db=db,
            document_id=document_record.id,
            law_office_id=52,
            new_status="REVIEWED",
        )

        assert result is None
        assert document_record.status == "UPLOADED"

    finally:
        if "document_record" in locals() and document_record.id is not None:
            db.delete(document_record)

        if "transaction_record" in locals() and transaction_record.id is not None:
            db.delete(transaction_record)

        if "client_record" in locals() and client_record.id is not None:
            db.delete(client_record)

        db.commit()
        db.close()


def test_transition_document_status_is_tenant_scoped():
    db = SessionLocal()

    try:
        user_record = db.get(User, 24)

        assert user_record is not None
        assert user_record.law_office_id == 52

        other_office = LawOffice(
            name="Other Workflow Service Office",
        )

        db.add(other_office)
        db.flush()

        other_user = User(
            law_office_id=other_office.id,
            email="other-workflow-service@example.com",
            full_name="Other Workflow Service User",
            role="STAFF",
            is_active=True,
        )

        db.add(other_user)
        db.flush()

        other_client = Client(
            law_office_id=other_office.id,
            full_name="Other Workflow Service Client",
        )

        db.add(other_client)
        db.flush()

        other_transaction = Transaction(
            law_office_id=other_office.id,
            client_id=other_client.id,
            transaction_type="ACKNOWLEDGMENT",
            status="DRAFT",
            title="Other Workflow Service Transaction",
            date_received=date(2026, 9, 13),
        )

        db.add(other_transaction)
        db.flush()

        other_document = Document(
            law_office_id=other_office.id,
            transaction_id=other_transaction.id,
            uploaded_by_user_id=other_user.id,
            filename="other-tenant-workflow.pdf",
            document_type="SOURCE_DOCUMENT",
            status="UPLOADED",
            storage_key="documents/other-tenant-workflow.pdf",
        )

        db.add(other_document)
        db.commit()
        db.refresh(other_document)

        result = transition_document_status(
            db=db,
            document_id=other_document.id,
            law_office_id=52,
            new_status="UNDER_REVIEW",
        )

        assert result is None
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

from datetime import date

from app.models.client import Client
from app.models.document import Document
from app.models.law_office import LawOffice
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.document import DocumentCreate
from app.services.document import (
    create_document,
    get_document,
    list_documents,
)


def test_create_document(db):
    office = LawOffice(name="Document Test Office")

    user = User(
        email="document-test@example.com",
        full_name="Document Test User",
        role="STAFF",
    )

    client = Client(
        full_name="Document Test Client",
    )

    transaction = Transaction(
        reference_number="DOC-001",
        transaction_type="ACKNOWLEDGMENT",
        status="DRAFT",
        title="Document Test Transaction",
        date_received=date(2026, 9, 13),
    )

    office.users.append(user)
    office.clients.append(client)
    office.transactions.append(transaction)
    client.transactions.append(transaction)

    db.add(office)
    db.flush()

    document_data = DocumentCreate(
        transaction_id=transaction.id,
        uploaded_by_user_id=user.id,
        filename="valid-id.pdf",
        document_type="VALID_ID",
        storage_key="documents/valid-id.pdf",
    )

    document = create_document(
        db=db,
        law_office_id=office.id,
        document_data=document_data,
    )

    assert document is not None
    assert isinstance(document, Document)
    assert document.law_office_id == office.id
    assert document.transaction_id == transaction.id
    assert document.uploaded_by_user_id == user.id
    assert document.filename == "valid-id.pdf"
    assert document.document_type == "VALID_ID"
    assert document.status == "UPLOADED"
    assert document.storage_key == "documents/valid-id.pdf"


def test_create_document_rejects_other_tenant_transaction(db):
    office_a = LawOffice(name="Document Tenant A")
    office_b = LawOffice(name="Document Tenant B")

    user_a = User(
        email="document-tenant-a@example.com",
        full_name="Tenant A User",
        role="STAFF",
    )

    client_b = Client(
        full_name="Tenant B Client",
    )

    transaction_b = Transaction(
        reference_number="DOC-B-001",
        transaction_type="ACKNOWLEDGMENT",
        status="DRAFT",
        title="Tenant B Transaction",
        date_received=date(2026, 9, 13),
    )

    office_a.users.append(user_a)
    office_b.clients.append(client_b)
    office_b.transactions.append(transaction_b)
    client_b.transactions.append(transaction_b)

    db.add_all([office_a, office_b])
    db.flush()

    document_data = DocumentCreate(
        transaction_id=transaction_b.id,
        uploaded_by_user_id=user_a.id,
        filename="cross-tenant.pdf",
        document_type="VALID_ID",
        storage_key="documents/cross-tenant.pdf",
    )

    document = create_document(
        db=db,
        law_office_id=office_a.id,
        document_data=document_data,
    )

    assert document is None


def test_create_document_rejects_other_tenant_user(db):
    office_a = LawOffice(name="Document User Tenant A")
    office_b = LawOffice(name="Document User Tenant B")

    user_b = User(
        email="document-user-tenant-b@example.com",
        full_name="Tenant B User",
        role="STAFF",
    )

    client_a = Client(
        full_name="Tenant A Client",
    )

    transaction_a = Transaction(
        reference_number="DOC-A-001",
        transaction_type="JURAT",
        status="DRAFT",
        title="Tenant A Transaction",
        date_received=date(2026, 9, 13),
    )

    office_b.users.append(user_b)
    office_a.clients.append(client_a)
    office_a.transactions.append(transaction_a)
    client_a.transactions.append(transaction_a)

    db.add_all([office_a, office_b])
    db.flush()

    document_data = DocumentCreate(
        transaction_id=transaction_a.id,
        uploaded_by_user_id=user_b.id,
        filename="cross-tenant-user.pdf",
        document_type="VALID_ID",
        storage_key="documents/cross-tenant-user.pdf",
    )

    document = create_document(
        db=db,
        law_office_id=office_a.id,
        document_data=document_data,
    )

    assert document is None


def test_get_document_is_tenant_scoped(db):
    office_a = LawOffice(name="Document Get Office A")
    office_b = LawOffice(name="Document Get Office B")

    user_a = User(
        email="document-get-a@example.com",
        full_name="Document Get User A",
        role="STAFF",
    )

    client_a = Client(
        full_name="Document Get Client A",
    )

    transaction_a = Transaction(
        reference_number="DOC-GET-001",
        transaction_type="ACKNOWLEDGMENT",
        status="DRAFT",
        title="Document Get Transaction",
        date_received=date(2026, 9, 13),
    )

    office_a.users.append(user_a)
    office_a.clients.append(client_a)
    office_a.transactions.append(transaction_a)
    client_a.transactions.append(transaction_a)

    db.add_all([office_a, office_b])
    db.flush()

    document_data = DocumentCreate(
        transaction_id=transaction_a.id,
        uploaded_by_user_id=user_a.id,
        filename="retrieval-test.pdf",
        document_type="SOURCE_DOCUMENT",
        storage_key="documents/retrieval-test.pdf",
    )

    document = create_document(
        db=db,
        law_office_id=office_a.id,
        document_data=document_data,
    )

    assert document is not None

    result = get_document(
        db=db,
        document_id=document.id,
        law_office_id=office_a.id,
    )

    assert result is not None
    assert result.id == document.id

    other_result = get_document(
        db=db,
        document_id=document.id,
        law_office_id=office_b.id,
    )

    assert other_result is None


def test_list_documents_is_tenant_scoped(db):
    office_a = LawOffice(name="Document List Office A")
    office_b = LawOffice(name="Document List Office B")

    user_a = User(
        email="document-list-a@example.com",
        full_name="Document List User A",
        role="STAFF",
    )

    user_b = User(
        email="document-list-b@example.com",
        full_name="Document List User B",
        role="STAFF",
    )

    client_a = Client(full_name="Document List Client A")
    client_b = Client(full_name="Document List Client B")

    transaction_a = Transaction(
        reference_number="DOC-LIST-A",
        transaction_type="ACKNOWLEDGMENT",
        status="DRAFT",
        title="Office A Transaction",
        date_received=date(2026, 9, 13),
    )

    transaction_b = Transaction(
        reference_number="DOC-LIST-B",
        transaction_type="JURAT",
        status="DRAFT",
        title="Office B Transaction",
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
            filename="office-a.pdf",
            document_type="VALID_ID",
            storage_key="documents/office-a.pdf",
        ),
    )

    document_b = create_document(
        db=db,
        law_office_id=office_b.id,
        document_data=DocumentCreate(
            transaction_id=transaction_b.id,
            uploaded_by_user_id=user_b.id,
            filename="office-b.pdf",
            document_type="SOURCE_DOCUMENT",
            storage_key="documents/office-b.pdf",
        ),
    )

    assert document_a is not None
    assert document_b is not None

    documents_a = list_documents(
        db=db,
        law_office_id=office_a.id,
    )

    assert len(documents_a) == 1
    assert documents_a[0].id == document_a.id

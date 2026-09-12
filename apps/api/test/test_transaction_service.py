from datetime import date

from app.models.client import Client
from app.models.law_office import LawOffice
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from app.services.transaction import (
    create_transaction,
    get_transaction,
    list_transactions,
    update_transaction,
)


def test_create_transaction(db):
    office = LawOffice(name="Transaction Create Test Office")

    client = Client(
        full_name="Transaction Test Client",
    )

    office.clients.append(client)

    db.add(office)
    db.flush()

    transaction_data = TransactionCreate(
        client_id=client.id,
        reference_number="REF-001",
        transaction_type="ACKNOWLEDGMENT",
        title="Test Transaction",
        description="Test description",
        date_received=date(2026, 9, 12),
    )

    transaction = create_transaction(
        db=db,
        law_office_id=office.id,
        transaction_data=transaction_data,
    )

    assert transaction is not None
    assert transaction.law_office_id == office.id
    assert transaction.client_id == client.id
    assert transaction.reference_number == "REF-001"
    assert transaction.transaction_type == "ACKNOWLEDGMENT"
    assert transaction.status == "DRAFT"
    assert transaction.title == "Test Transaction"


def test_create_transaction_rejects_other_tenant_client(db):
    office_a = LawOffice(name="Transaction Tenant A")
    office_b = LawOffice(name="Transaction Tenant B")

    client_b = Client(
        full_name="Tenant B Client",
    )

    office_b.clients.append(client_b)

    db.add_all([office_a, office_b])
    db.flush()

    transaction_data = TransactionCreate(
        client_id=client_b.id,
        transaction_type="ACKNOWLEDGMENT",
        title="Cross Tenant Transaction",
        date_received=date(2026, 9, 12),
    )

    transaction = create_transaction(
        db=db,
        law_office_id=office_a.id,
        transaction_data=transaction_data,
    )

    assert transaction is None


def test_get_transaction_is_tenant_scoped(db):
    office_a = LawOffice(name="Transaction Get Office A")
    office_b = LawOffice(name="Transaction Get Office B")

    client_a = Client(full_name="Transaction Client A")
    office_a.clients.append(client_a)

    db.add_all([office_a, office_b])
    db.flush()

    transaction_data = TransactionCreate(
        client_id=client_a.id,
        transaction_type="ACKNOWLEDGMENT",
        title="Tenant Scoped Transaction",
        date_received=date(2026, 9, 12),
    )

    transaction = create_transaction(
        db=db,
        law_office_id=office_a.id,
        transaction_data=transaction_data,
    )

    assert transaction is not None

    result = get_transaction(
        db=db,
        transaction_id=transaction.id,
        law_office_id=office_a.id,
    )

    assert result is not None
    assert result.id == transaction.id

    other_result = get_transaction(
        db=db,
        transaction_id=transaction.id,
        law_office_id=office_b.id,
    )

    assert other_result is None


def test_list_transactions_is_tenant_scoped(db):
    office_a = LawOffice(name="Transaction List Office A")
    office_b = LawOffice(name="Transaction List Office B")

    client_a = Client(full_name="Transaction List Client A")
    client_b = Client(full_name="Transaction List Client B")

    office_a.clients.append(client_a)
    office_b.clients.append(client_b)

    db.add_all([office_a, office_b])
    db.flush()

    transaction_a = create_transaction(
        db=db,
        law_office_id=office_a.id,
        transaction_data=TransactionCreate(
            client_id=client_a.id,
            transaction_type="ACKNOWLEDGMENT",
            title="Office A Transaction",
            date_received=date(2026, 9, 12),
        ),
    )

    transaction_b = create_transaction(
        db=db,
        law_office_id=office_b.id,
        transaction_data=TransactionCreate(
            client_id=client_b.id,
            transaction_type="JURAT",
            title="Office B Transaction",
            date_received=date(2026, 9, 12),
        ),
    )

    assert transaction_a is not None
    assert transaction_b is not None

    transactions_a = list_transactions(
        db=db,
        law_office_id=office_a.id,
    )

    assert len(transactions_a) == 1
    assert transactions_a[0].id == transaction_a.id


def test_update_transaction(db):
    office = LawOffice(name="Transaction Update Test Office")

    client = Client(
        full_name="Transaction Update Client",
    )

    office.clients.append(client)

    db.add(office)
    db.flush()

    transaction = create_transaction(
        db=db,
        law_office_id=office.id,
        transaction_data=TransactionCreate(
            client_id=client.id,
            reference_number="REF-OLD",
            transaction_type="ACKNOWLEDGMENT",
            title="Original Transaction",
            description="Original description",
            date_received=date(2026, 9, 12),
        ),
    )

    assert transaction is not None

    transaction_data = TransactionUpdate(
        reference_number="REF-NEW",
        transaction_type="JURAT",
        status="COMPLETED",
        title="Updated Transaction",
        description="Updated description",
        date_received=date(2026, 9, 12),
        date_completed=date(2026, 9, 13),
    )

    updated_transaction = update_transaction(
        db=db,
        transaction_id=transaction.id,
        law_office_id=office.id,
        transaction_data=transaction_data,
    )

    assert updated_transaction is not None
    assert updated_transaction.client_id == client.id
    assert updated_transaction.reference_number == "REF-NEW"
    assert updated_transaction.transaction_type == "JURAT"
    assert updated_transaction.status == "COMPLETED"
    assert updated_transaction.title == "Updated Transaction"
    assert updated_transaction.description == "Updated description"
    assert updated_transaction.date_completed == date(2026, 9, 13)


def test_update_transaction_is_tenant_scoped(db):
    office_a = LawOffice(name="Transaction Update Tenant A")
    office_b = LawOffice(name="Transaction Update Tenant B")

    client_a = Client(full_name="Transaction Update Client A")
    office_a.clients.append(client_a)

    db.add_all([office_a, office_b])
    db.flush()

    transaction = create_transaction(
        db=db,
        law_office_id=office_a.id,
        transaction_data=TransactionCreate(
            client_id=client_a.id,
            transaction_type="ACKNOWLEDGMENT",
            title="Original Transaction",
            date_received=date(2026, 9, 12),
        ),
    )

    assert transaction is not None

    transaction_data = TransactionUpdate(
        transaction_type="JURAT",
        status="COMPLETED",
        title="Should Not Update",
        date_received=date(2026, 9, 12),
    )

    updated_transaction = update_transaction(
        db=db,
        transaction_id=transaction.id,
        law_office_id=office_b.id,
        transaction_data=transaction_data,
    )

    assert updated_transaction is None

    db.refresh(transaction)

    assert transaction.title == "Original Transaction"
    assert transaction.status == "DRAFT"

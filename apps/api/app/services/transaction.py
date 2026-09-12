from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionUpdate


def create_transaction(
    db: Session,
    law_office_id: int,
    transaction_data: TransactionCreate,
) -> Transaction | None:
    client = (
        db.query(Client)
        .filter(
            Client.id == transaction_data.client_id,
            Client.law_office_id == law_office_id,
        )
        .first()
    )

    if client is None:
        return None

    transaction = Transaction(
        law_office_id=law_office_id,
        client_id=transaction_data.client_id,
        reference_number=transaction_data.reference_number,
        transaction_type=transaction_data.transaction_type,
        status=transaction_data.status,
        title=transaction_data.title,
        description=transaction_data.description,
        date_received=transaction_data.date_received,
        date_completed=transaction_data.date_completed,
    )

    db.add(transaction)
    db.flush()
    db.refresh(transaction)

    return transaction


def get_transaction(
    db: Session,
    transaction_id: int,
    law_office_id: int,
) -> Transaction | None:
    return (
        db.query(Transaction)
        .filter(
            Transaction.id == transaction_id,
            Transaction.law_office_id == law_office_id,
        )
        .first()
    )


def list_transactions(
    db: Session,
    law_office_id: int,
) -> list[Transaction]:
    return (
        db.query(Transaction)
        .filter(Transaction.law_office_id == law_office_id)
        .order_by(Transaction.id)
        .all()
    )


def update_transaction(
    db: Session,
    transaction_id: int,
    law_office_id: int,
    transaction_data: TransactionUpdate,
) -> Transaction | None:
    transaction = (
        db.query(Transaction)
        .filter(
            Transaction.id == transaction_id,
            Transaction.law_office_id == law_office_id,
        )
        .first()
    )

    if transaction is None:
        return None

    transaction.reference_number = transaction_data.reference_number
    transaction.transaction_type = transaction_data.transaction_type
    transaction.status = transaction_data.status
    transaction.title = transaction_data.title
    transaction.description = transaction_data.description
    transaction.date_received = transaction_data.date_received
    transaction.date_completed = transaction_data.date_completed

    db.flush()
    db.refresh(transaction)

    return transaction

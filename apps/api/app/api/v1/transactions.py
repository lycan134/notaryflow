from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.current_user import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.transaction import (
    TransactionCreate,
    TransactionResponse,
    TransactionUpdate,
)
from app.services.transaction import (
    create_transaction,
    get_transaction,
    list_transactions,
    update_transaction,
)


router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
)


@router.post(
    "",
    response_model=TransactionResponse,
    status_code=201,
)
def create_transaction_endpoint(
    transaction_data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transaction = create_transaction(
        db=db,
        law_office_id=current_user.law_office_id,
        transaction_data=transaction_data,
    )

    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Client not found.",
        )

    db.commit()
    db.refresh(transaction)

    return transaction


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
)
def get_transaction_endpoint(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transaction = get_transaction(
        db=db,
        transaction_id=transaction_id,
        law_office_id=current_user.law_office_id,
    )

    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found.",
        )

    return transaction


@router.get(
    "",
    response_model=list[TransactionResponse],
)
def list_transactions_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_transactions(
        db=db,
        law_office_id=current_user.law_office_id,
    )


@router.put(
    "/{transaction_id}",
    response_model=TransactionResponse,
)
def update_transaction_endpoint(
    transaction_id: int,
    transaction_data: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transaction = update_transaction(
        db=db,
        transaction_id=transaction_id,
        law_office_id=current_user.law_office_id,
        transaction_data=transaction_data,
    )

    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found.",
        )

    db.commit()
    db.refresh(transaction)

    return transaction

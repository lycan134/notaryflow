from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.current_user import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.client import ClientCreate, ClientResponse
from app.services.client import create_client, get_client


router = APIRouter(
    prefix="/clients",
    tags=["clients"],
)


@router.post(
    "",
    response_model=ClientResponse,
    status_code=201,
)
def create_client_endpoint(
    client_data: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    client = create_client(
        db=db,
        law_office_id=current_user.law_office_id,
        client_data=client_data,
    )

    db.commit()
    db.refresh(client)

    return client


@router.get(
    "/{client_id}",
    response_model=ClientResponse,
)
def get_client_endpoint(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    client = get_client(
        db=db,
        client_id=client_id,
        law_office_id=current_user.law_office_id,
    )

    if client is None:
        raise HTTPException(
            status_code=404,
            detail="Client not found.",
        )

    return client

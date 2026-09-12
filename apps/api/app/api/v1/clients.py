from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.client import ClientCreate, ClientResponse
from app.services.client import create_client
from app.core.config import settings


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
):
    development_law_office_id = settings.development_law_office_id

    client = create_client(
        db=db,
        law_office_id=development_law_office_id,
        client_data=client_data,
    )

    db.commit()
    db.refresh(client)

    return client
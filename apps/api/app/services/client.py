from sqlalchemy.orm import Session

from app.models.client import Client
from app.schemas.client import ClientCreate


def create_client(
    db: Session,
    law_office_id: int,
    client_data: ClientCreate,
) -> Client:
    client = Client(
        law_office_id=law_office_id,
        full_name=client_data.full_name,
        address=client_data.address,
        contact_number=client_data.contact_number,
        email=client_data.email,
    )

    db.add(client)
    db.flush()
    db.refresh(client)

    return client


def get_client(
    db: Session,
    client_id: int,
    law_office_id: int,
) -> Client | None:
    return (
        db.query(Client)
        .filter(
            Client.id == client_id,
            Client.law_office_id == law_office_id,
        )
        .first()
    )
from app.models.client import Client
from app.models.law_office import LawOffice
from app.schemas.client import ClientCreate
from app.services.client import create_client


def test_create_client(db):
    office = LawOffice(name="Service Test Office")
    db.add(office)
    db.flush()

    client_data = ClientCreate(
        full_name="Pedro Reyes",
        address="Davao City",
        contact_number="09191234567",
        email="pedro@example.com",
    )

    client = create_client(
        db=db,
        law_office_id=office.id,
        client_data=client_data,
    )

    assert client.id is not None
    assert client.law_office_id == office.id
    assert client.full_name == "Pedro Reyes"
    assert client.email == "pedro@example.com"

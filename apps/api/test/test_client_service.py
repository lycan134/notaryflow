from app.models.client import Client
from app.models.law_office import LawOffice
from app.schemas.client import ClientCreate
from app.services.client import create_client, get_client


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


def test_get_client_is_tenant_scoped(db):
    office_a = LawOffice(name="Tenant A")
    office_b = LawOffice(name="Tenant B")

    db.add_all([office_a, office_b])
    db.flush()

    client = Client(
        law_office_id=office_a.id,
        full_name="Tenant A Client",
    )

    db.add(client)
    db.flush()

    client_from_a = get_client(
        db=db,
        client_id=client.id,
        law_office_id=office_a.id,
    )

    client_from_b = get_client(
        db=db,
        client_id=client.id,
        law_office_id=office_b.id,
    )

    assert client_from_a is not None
    assert client_from_a.full_name == "Tenant A Client"
    assert client_from_b is None

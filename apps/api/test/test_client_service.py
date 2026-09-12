from app.models.client import Client
from app.models.law_office import LawOffice
from app.schemas.client import ClientCreate, ClientUpdate
from app.services.client import (
    create_client,
    get_client,
    list_clients,
    update_client,
)


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


def test_list_clients_is_tenant_scoped(db):
    office_a = LawOffice(name="List Tenant A")
    office_b = LawOffice(name="List Tenant B")

    db.add_all([office_a, office_b])
    db.flush()

    client_a1 = Client(
        law_office_id=office_a.id,
        full_name="Tenant A Client 1",
    )
    client_a2 = Client(
        law_office_id=office_a.id,
        full_name="Tenant A Client 2",
    )
    client_b = Client(
        law_office_id=office_b.id,
        full_name="Tenant B Client",
    )

    db.add_all([client_a1, client_a2, client_b])
    db.flush()

    clients_from_a = list_clients(
        db=db,
        law_office_id=office_a.id,
    )

    clients_from_b = list_clients(
        db=db,
        law_office_id=office_b.id,
    )

    assert [client.full_name for client in clients_from_a] == [
        "Tenant A Client 1",
        "Tenant A Client 2",
    ]

    assert [client.full_name for client in clients_from_b] == [
        "Tenant B Client",
    ]


def test_update_client(db):
    office = LawOffice(name="Update Test Office")

    client = Client(
        full_name="Original Client",
        address="Original Address",
        contact_number="09170000000",
        email="original@example.com",
    )

    office.clients.append(client)

    db.add(office)
    db.flush()

    client_data = ClientUpdate(
        full_name="Updated Client",
        address="Updated Address",
        contact_number="09179999999",
        email="updated@example.com",
    )

    updated_client = update_client(
        db=db,
        client_id=client.id,
        law_office_id=office.id,
        client_data=client_data,
    )

    assert updated_client is not None
    assert updated_client.full_name == "Updated Client"
    assert updated_client.address == "Updated Address"
    assert updated_client.contact_number == "09179999999"
    assert updated_client.email == "updated@example.com"


def test_update_client_is_tenant_scoped(db):
    office_a = LawOffice(name="Update Tenant A")
    office_b = LawOffice(name="Update Tenant B")

    client = Client(
        full_name="Tenant A Client",
    )

    office_a.clients.append(client)

    db.add_all([office_a, office_b])
    db.flush()

    client_data = ClientUpdate(
        full_name="Malicious Update",
        address="Changed Address",
    )

    updated_client = update_client(
        db=db,
        client_id=client.id,
        law_office_id=office_b.id,
        client_data=client_data,
    )

    assert updated_client is None

    db.refresh(client)

    assert client.full_name == "Tenant A Client"

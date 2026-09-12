from fastapi.testclient import TestClient

from app.db.database import SessionLocal
from app.main import app
from app.models.client import Client
from app.models.law_office import LawOffice

client = TestClient(app)


def test_create_client_endpoint():
    response = client.post(
        "/api/v1/clients",
        json={
            "full_name": "API Test Client",
            "address": "Davao City",
            "contact_number": "09170000000",
            "email": "api-test@example.com",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] is not None
    assert data["law_office_id"] is not None
    assert data["full_name"] == "API Test Client"
    assert data["email"] == "api-test@example.com"


def test_get_client_endpoint():
    db = SessionLocal()

    try:
        client_record = Client(
            law_office_id=52,
            full_name="GET API Test Client",
            address="Davao City",
            contact_number="09171111111",
            email="get-api-test@example.com",
        )

        db.add(client_record)
        db.commit()
        db.refresh(client_record)

        response = client.get(
            f"/api/v1/clients/{client_record.id}"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == client_record.id
        assert data["law_office_id"] == 52
        assert data["full_name"] == "GET API Test Client"
        assert data["email"] == "get-api-test@example.com"

    finally:
        if "client_record" in locals() and client_record.id is not None:
            db.delete(client_record)
            db.commit()

        db.close()


def test_get_client_endpoint_blocks_other_tenant():
    db = SessionLocal()

    try:
        other_office = LawOffice(
            name="Other API Test Office",
        )
        db.add(other_office)
        db.flush()

        client_record = Client(
            law_office_id=other_office.id,
            full_name="Other Tenant Client",
        )

        db.add(client_record)
        db.commit()
        db.refresh(client_record)

        response = client.get(
            f"/api/v1/clients/{client_record.id}"
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Client not found."

    finally:
        if "client_record" in locals() and client_record.id is not None:
            db.delete(client_record)

        if "other_office" in locals() and other_office.id is not None:
            db.delete(other_office)

        db.commit()
        db.close()


def test_list_clients_endpoint():
    db = SessionLocal()

    try:
        client_a = Client(
            law_office_id=52,
            full_name="List API Client A",
        )
        client_b = Client(
            law_office_id=52,
            full_name="List API Client B",
        )

        db.add_all([client_a, client_b])
        db.commit()

        response = client.get("/api/v1/clients")

        assert response.status_code == 200

        data = response.json()

        returned_names = [item["full_name"] for item in data]

        assert "List API Client A" in returned_names
        assert "List API Client B" in returned_names

    finally:
        if "client_a" in locals() and client_a.id is not None:
            db.delete(client_a)

        if "client_b" in locals() and client_b.id is not None:
            db.delete(client_b)

        db.commit()
        db.close()


def test_list_clients_endpoint_excludes_other_tenant():
    db = SessionLocal()

    try:
        other_office = LawOffice(
            name="Other List API Test Office",
        )
        db.add(other_office)
        db.flush()

        other_client = Client(
            law_office_id=other_office.id,
            full_name="Other Tenant List Client",
        )

        db.add(other_client)
        db.commit()

        response = client.get("/api/v1/clients")

        assert response.status_code == 200

        data = response.json()

        returned_names = [item["full_name"] for item in data]

        assert "Other Tenant List Client" not in returned_names

    finally:
        if "other_client" in locals() and other_client.id is not None:
            db.delete(other_client)

        if "other_office" in locals() and other_office.id is not None:
            db.delete(other_office)

        db.commit()
        db.close()

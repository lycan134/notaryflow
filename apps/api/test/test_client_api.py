from fastapi.testclient import TestClient

from app.main import app


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

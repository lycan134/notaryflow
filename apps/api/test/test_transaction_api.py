from datetime import date

from fastapi.testclient import TestClient

from app.db.database import SessionLocal
from app.main import app
from app.models.client import Client
from app.models.law_office import LawOffice
from app.models.transaction import Transaction


client = TestClient(app)


def test_create_transaction_endpoint():
    db = SessionLocal()

    try:
        client_record = Client(
            law_office_id=52,
            full_name="Transaction API Create Client",
        )

        db.add(client_record)
        db.commit()
        db.refresh(client_record)

        response = client.post(
            "/api/v1/transactions",
            json={
                "client_id": client_record.id,
                "reference_number": "API-REF-001",
                "transaction_type": "ACKNOWLEDGMENT",
                "title": "API Test Transaction",
                "description": "API test description",
                "date_received": "2026-09-12",
            },
        )

        assert response.status_code == 201

        data = response.json()

        assert data["id"] is not None
        assert data["law_office_id"] == 52
        assert data["client_id"] == client_record.id
        assert data["reference_number"] == "API-REF-001"
        assert data["transaction_type"] == "ACKNOWLEDGMENT"
        assert data["status"] == "DRAFT"
        assert data["title"] == "API Test Transaction"

        transaction_record = db.get(Transaction, data["id"])

    finally:
        if "transaction_record" in locals() and transaction_record is not None:
            db.delete(transaction_record)

        if "client_record" in locals() and client_record.id is not None:
            db.delete(client_record)

        db.commit()
        db.close()


def test_create_transaction_endpoint_blocks_other_tenant_client():
    db = SessionLocal()

    try:
        other_office = LawOffice(
            name="Other Transaction Create API Office",
        )
        db.add(other_office)
        db.flush()

        client_record = Client(
            law_office_id=other_office.id,
            full_name="Other Tenant Transaction Client",
        )

        db.add(client_record)
        db.commit()
        db.refresh(client_record)

        response = client.post(
            "/api/v1/transactions",
            json={
                "client_id": client_record.id,
                "transaction_type": "ACKNOWLEDGMENT",
                "title": "Should Not Create",
                "date_received": "2026-09-12",
            },
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


def test_get_transaction_endpoint():
    db = SessionLocal()

    try:
        client_record = Client(
            law_office_id=52,
            full_name="Transaction GET API Client",
        )

        db.add(client_record)
        db.flush()

        transaction_record = Transaction(
            law_office_id=52,
            client_id=client_record.id,
            reference_number="GET-REF-001",
            transaction_type="ACKNOWLEDGMENT",
            status="DRAFT",
            title="GET API Transaction",
            date_received=date(2026, 9, 12),
        )

        db.add(transaction_record)
        db.commit()
        db.refresh(transaction_record)

        response = client.get(
            f"/api/v1/transactions/{transaction_record.id}"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == transaction_record.id
        assert data["law_office_id"] == 52
        assert data["client_id"] == client_record.id
        assert data["title"] == "GET API Transaction"

    finally:
        if "transaction_record" in locals() and transaction_record.id is not None:
            db.delete(transaction_record)

        if "client_record" in locals() and client_record.id is not None:
            db.delete(client_record)

        db.commit()
        db.close()


def test_get_transaction_endpoint_blocks_other_tenant():
    db = SessionLocal()

    try:
        other_office = LawOffice(
            name="Other Transaction GET API Office",
        )
        db.add(other_office)
        db.flush()

        client_record = Client(
            law_office_id=other_office.id,
            full_name="Other Tenant GET Client",
        )

        db.add(client_record)
        db.flush()

        transaction_record = Transaction(
            law_office_id=other_office.id,
            client_id=client_record.id,
            transaction_type="ACKNOWLEDGMENT",
            status="DRAFT",
            title="Other Tenant Transaction",
            date_received=date(2026, 9, 12),
        )

        db.add(transaction_record)
        db.commit()
        db.refresh(transaction_record)

        response = client.get(
            f"/api/v1/transactions/{transaction_record.id}"
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Transaction not found."

    finally:
        if "transaction_record" in locals() and transaction_record.id is not None:
            db.delete(transaction_record)

        if "client_record" in locals() and client_record.id is not None:
            db.delete(client_record)

        if "other_office" in locals() and other_office.id is not None:
            db.delete(other_office)

        db.commit()
        db.close()


def test_list_transactions_endpoint():
    db = SessionLocal()

    try:
        client_a = Client(
            law_office_id=52,
            full_name="Transaction List API Client A",
        )
        client_b = Client(
            law_office_id=52,
            full_name="Transaction List API Client B",
        )

        db.add_all([client_a, client_b])
        db.flush()

        transaction_a = Transaction(
            law_office_id=52,
            client_id=client_a.id,
            transaction_type="ACKNOWLEDGMENT",
            status="DRAFT",
            title="List API Transaction A",
            date_received=date(2026, 9, 12),
        )

        transaction_b = Transaction(
            law_office_id=52,
            client_id=client_b.id,
            transaction_type="JURAT",
            status="IN_PROGRESS",
            title="List API Transaction B",
            date_received=date(2026, 9, 12),
        )

        db.add_all([transaction_a, transaction_b])
        db.commit()

        response = client.get("/api/v1/transactions")

        assert response.status_code == 200

        data = response.json()

        returned_titles = [item["title"] for item in data]

        assert "List API Transaction A" in returned_titles
        assert "List API Transaction B" in returned_titles

    finally:
        if "transaction_a" in locals() and transaction_a.id is not None:
            db.delete(transaction_a)

        if "transaction_b" in locals() and transaction_b.id is not None:
            db.delete(transaction_b)

        if "client_a" in locals() and client_a.id is not None:
            db.delete(client_a)

        if "client_b" in locals() and client_b.id is not None:
            db.delete(client_b)

        db.commit()
        db.close()


def test_list_transactions_endpoint_excludes_other_tenant():
    db = SessionLocal()

    try:
        other_office = LawOffice(
            name="Other Transaction List API Office",
        )
        db.add(other_office)
        db.flush()

        other_client = Client(
            law_office_id=other_office.id,
            full_name="Other Tenant List Transaction Client",
        )

        db.add(other_client)
        db.flush()

        other_transaction = Transaction(
            law_office_id=other_office.id,
            client_id=other_client.id,
            transaction_type="ACKNOWLEDGMENT",
            status="DRAFT",
            title="Other Tenant List Transaction",
            date_received=date(2026, 9, 12),
        )

        db.add(other_transaction)
        db.commit()

        response = client.get("/api/v1/transactions")

        assert response.status_code == 200

        data = response.json()

        returned_titles = [item["title"] for item in data]

        assert "Other Tenant List Transaction" not in returned_titles

    finally:
        if "other_transaction" in locals() and other_transaction.id is not None:
            db.delete(other_transaction)

        if "other_client" in locals() and other_client.id is not None:
            db.delete(other_client)

        if "other_office" in locals() and other_office.id is not None:
            db.delete(other_office)

        db.commit()
        db.close()


def test_update_transaction_endpoint():
    db = SessionLocal()

    try:
        client_record = Client(
            law_office_id=52,
            full_name="Transaction Update API Client",
        )

        db.add(client_record)
        db.flush()

        transaction_record = Transaction(
            law_office_id=52,
            client_id=client_record.id,
            reference_number="UPDATE-OLD",
            transaction_type="ACKNOWLEDGMENT",
            status="DRAFT",
            title="Original API Transaction",
            description="Original description",
            date_received=date(2026, 9, 12),
        )

        db.add(transaction_record)
        db.commit()
        db.refresh(transaction_record)

        response = client.put(
            f"/api/v1/transactions/{transaction_record.id}",
            json={
                "reference_number": "UPDATE-NEW",
                "transaction_type": "JURAT",
                "status": "COMPLETED",
                "title": "Updated API Transaction",
                "description": "Updated description",
                "date_received": "2026-09-12",
                "date_completed": "2026-09-13",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == transaction_record.id
        assert data["law_office_id"] == 52
        assert data["client_id"] == client_record.id
        assert data["reference_number"] == "UPDATE-NEW"
        assert data["transaction_type"] == "JURAT"
        assert data["status"] == "COMPLETED"
        assert data["title"] == "Updated API Transaction"
        assert data["description"] == "Updated description"
        assert data["date_completed"] == "2026-09-13"

    finally:
        if "transaction_record" in locals() and transaction_record.id is not None:
            db.delete(transaction_record)

        if "client_record" in locals() and client_record.id is not None:
            db.delete(client_record)

        db.commit()
        db.close()


def test_update_transaction_endpoint_blocks_other_tenant():
    db = SessionLocal()

    try:
        other_office = LawOffice(
            name="Other Transaction Update API Office",
        )
        db.add(other_office)
        db.flush()

        client_record = Client(
            law_office_id=other_office.id,
            full_name="Other Tenant Update Transaction Client",
        )

        db.add(client_record)
        db.flush()

        transaction_record = Transaction(
            law_office_id=other_office.id,
            client_id=client_record.id,
            transaction_type="ACKNOWLEDGMENT",
            status="DRAFT",
            title="Other Tenant Original Transaction",
            date_received=date(2026, 9, 12),
        )

        db.add(transaction_record)
        db.commit()
        db.refresh(transaction_record)

        response = client.put(
            f"/api/v1/transactions/{transaction_record.id}",
            json={
                "transaction_type": "JURAT",
                "status": "COMPLETED",
                "title": "Should Not Update",
                "date_received": "2026-09-12",
            },
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Transaction not found."

    finally:
        if "transaction_record" in locals() and transaction_record.id is not None:
            db.delete(transaction_record)

        if "client_record" in locals() and client_record.id is not None:
            db.delete(client_record)

        if "other_office" in locals() and other_office.id is not None:
            db.delete(other_office)

        db.commit()
        db.close()

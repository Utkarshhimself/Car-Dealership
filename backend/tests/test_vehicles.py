from datetime import UTC, datetime
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.vehicle import Vehicle

PASSWORD = "correct-horse-battery-staple"


def authenticated_headers(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/api/auth/register",
        json={"email": "inventory@example.com", "password": PASSWORD},
    )
    assert response.status_code == 201
    response = client.post(
        "/api/auth/login",
        json={"email": "inventory@example.com", "password": PASSWORD},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def add_vehicle(
    db_session: Session,
    make: str,
    model: str,
    category: str,
    price: str,
    quantity: int,
) -> Vehicle:
    vehicle = Vehicle(
        make=make,
        model=model,
        category=category,
        price=Decimal(price),
        quantity=quantity,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db_session.add(vehicle)
    db_session.commit()
    db_session.refresh(vehicle)
    return vehicle


def test_inventory_requires_authentication(client: TestClient) -> None:
    assert client.get("/api/vehicles").status_code == 401


def test_lists_and_filters_inventory(client: TestClient, db_session: Session) -> None:
    rav4 = add_vehicle(db_session, "Toyota", "RAV4", "SUV", "35000.00", 3)
    add_vehicle(db_session, "Toyota", "Corolla", "Sedan", "24000.00", 5)
    add_vehicle(db_session, "Honda", "CR-V", "SUV", "33000.00", 2)

    response = client.get(
        "/api/vehicles",
        params={"make": "toy", "category": "suv", "min_price": "30000", "max_price": "40000"},
        headers=authenticated_headers(client),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["page"] == 1
    assert body["page_size"] == 20
    assert body["items"][0]["id"] == str(rav4.id)
    assert body["items"][0]["price"] == "35000.00"


def test_inventory_pagination_and_empty_results(client: TestClient, db_session: Session) -> None:
    add_vehicle(db_session, "Toyota", "RAV4", "SUV", "35000.00", 3)
    add_vehicle(db_session, "Honda", "Civic", "Sedan", "28000.00", 1)
    headers = authenticated_headers(client)

    page = client.get("/api/vehicles", params={"page": 2, "page_size": 1}, headers=headers)
    empty = client.get("/api/vehicles", params={"make": "Tesla"}, headers=headers)

    assert page.status_code == 200
    assert page.json()["total"] == 2
    assert len(page.json()["items"]) == 1
    assert empty.status_code == 200
    assert empty.json()["items"] == []
    assert empty.json()["total"] == 0


def test_inventory_rejects_invalid_filters(client: TestClient) -> None:
    headers = authenticated_headers(client)

    assert client.get("/api/vehicles", params={"page": 0}, headers=headers).status_code == 422
    assert client.get("/api/vehicles", params={"page_size": 101}, headers=headers).status_code == 422
    assert client.get("/api/vehicles", params={"min_price": 0}, headers=headers).status_code == 422

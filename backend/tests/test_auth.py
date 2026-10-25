from datetime import UTC, datetime, timedelta

import jwt
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import require_admin
from app.core.config import settings
from app.core.security import verify_password
from app.models.user import User

PASSWORD = "correct-horse-battery-staple"


def register(client: TestClient, email: str = "customer@example.com"):
    return client.post("/api/auth/register", json={"email": email, "password": PASSWORD})


def login(client: TestClient, email: str = "customer@example.com", password: str = PASSWORD) -> str:
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_registers_customer_with_hashed_password(client: TestClient, db_session: Session) -> None:
    response = register(client, "Customer@Example.COM")

    assert response.status_code == 201
    assert response.json()["email"] == "customer@example.com"
    assert response.json()["role"] == "customer"
    assert "password" not in response.json()
    assert "password_hash" not in response.json()

    user = db_session.scalar(select(User).where(User.email == "customer@example.com"))
    assert user is not None
    assert user.password_hash != PASSWORD
    assert verify_password(PASSWORD, user.password_hash)


def test_rejects_duplicate_email_case_insensitively(client: TestClient) -> None:
    assert register(client, "Customer@Example.com").status_code == 201

    response = register(client, "CUSTOMER@example.COM")

    assert response.status_code == 409
    assert response.json()["detail"] == "Email is already registered"


@pytest.mark.parametrize(
    "payload",
    [
        {"email": "invalid-email", "password": PASSWORD},
        {"email": "customer@example.com", "password": "too-short"},
        {"email": "customer@example.com", "password": "x" * 129},
    ],
)
def test_rejects_invalid_registration_input(client: TestClient, payload: dict[str, str]) -> None:
    assert client.post("/api/auth/register", json=payload).status_code == 422


def test_login_returns_access_token_and_me_returns_current_user(client: TestClient) -> None:
    assert register(client).status_code == 201

    token = login(client)
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["email"] == "customer@example.com"
    assert response.json()["role"] == "customer"


@pytest.mark.parametrize(
    "email,password",
    [
        ("missing@example.com", PASSWORD),
        ("customer@example.com", "not-the-correct-password"),
    ],
)
def test_login_rejects_invalid_credentials(client: TestClient, email: str, password: str) -> None:
    assert register(client).status_code == 201

    response = client.post("/api/auth/login", json={"email": email, "password": password})

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_me_rejects_missing_or_malformed_token(client: TestClient) -> None:
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer not-a-token"}).status_code == 401


def test_me_rejects_token_missing_required_access_claim(client: TestClient) -> None:
    now = datetime.now(UTC)
    token = jwt.encode(
        {"sub": "00000000-0000-0000-0000-000000000000", "iat": now, "exp": now + timedelta(1)},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


def test_me_rejects_non_access_token(client: TestClient) -> None:
    now = datetime.now(UTC)
    token = jwt.encode(
        {
            "sub": "00000000-0000-0000-0000-000000000000",
            "type": "refresh",
            "iat": now,
            "exp": now + timedelta(1),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


def test_admin_guard_rejects_customer_and_allows_admin(client: TestClient, db_session: Session) -> None:
    assert register(client).status_code == 201
    customer = db_session.scalar(select(User).where(User.email == "customer@example.com"))
    assert customer is not None

    with pytest.raises(HTTPException) as exception:
        require_admin(customer)
    assert exception.value.status_code == 403

    customer.role = "admin"
    assert require_admin(customer) is customer

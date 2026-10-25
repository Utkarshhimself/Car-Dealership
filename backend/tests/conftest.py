"""Shared isolated database and API client fixtures."""

import os
from collections.abc import Generator

os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_NAME", "car_dealership_test")
os.environ.setdefault("DB_USER", "test_user")
os.environ.setdefault("DB_PASSWORD", "test_password")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-that-is-long-enough-for-testing")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models
from app.db.base import Base
from app.db.session import get_db
from app.main import app

test_database_url = os.getenv("TEST_DATABASE_URL", "sqlite://")
test_engine = create_engine(
    test_database_url,
    connect_args={"check_same_thread": False} if test_database_url == "sqlite://" else {},
    poolclass=StaticPool if test_database_url == "sqlite://" else None,
)
TestingSessionLocal = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)


@pytest.fixture(autouse=True)
def database() -> Generator[None, None, None]:
    if test_database_url == "sqlite://":
        Base.metadata.drop_all(bind=test_engine)
        Base.metadata.create_all(bind=test_engine)
    else:
        with test_engine.begin() as connection:
            for table in reversed(Base.metadata.sorted_tables):
                connection.execute(table.delete())

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

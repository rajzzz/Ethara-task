from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, create_engine

from app import db
from app.main import app


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    db.engine = test_engine
    SQLModel.metadata.create_all(test_engine)

    with TestClient(app) as test_client:
        yield test_client

    SQLModel.metadata.drop_all(test_engine)

from __future__ import annotations

import os

os.environ["DATABASE_URL"] = "sqlite:///./backend-test.db"
os.environ["OPS_TOKEN"] = "test-ops-token"
os.environ.pop("LOG_FILE", None)
os.environ.pop("OTEL_EXPORTER_OTLP_ENDPOINT", None)

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def clean_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def valid_csv() -> bytes:
    return (
        b"observation_id,predicted_pd,default_flag\n"
        b"A,0.10,0\n"
        b"B,0.20,0\n"
        b"C,0.80,1\n"
        b"D,0.90,1\n"
    )


import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.store import store


@pytest.fixture(autouse=True)
def reset_store():
    """Reset in-memory store before each test for isolation."""
    store.reset()
    yield
    store.reset()


@pytest.fixture
def client():
    return TestClient(app)

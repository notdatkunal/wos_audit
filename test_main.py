import pytest
from fastapi.testclient import TestClient
from main import app
from database import get_db
from unittest.mock import MagicMock

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(autouse=True)
def mock_db_dependency():
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    yield mock_db
    app.dependency_overrides.clear()

def test_read_test_endpoint_no_auth(client, mock_db_dependency):
    # Mock the DB execute response
    mock_result = MagicMock()
    mock_result.scalar.return_value = 1
    mock_db_dependency.execute.return_value = mock_result
    
    response = client.get("/test")
    assert response.status_code == 200
    assert response.json()["message"] == "test successful"

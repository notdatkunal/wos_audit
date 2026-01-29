import pytest
from fastapi.testclient import TestClient
from main import app
from database import get_db
import models, auth
from unittest.mock import MagicMock
from jose import jwt
import os

client = TestClient(app)

@pytest.fixture(autouse=True)
def mock_db_dependency():
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    yield mock_db
    app.dependency_overrides.clear()

def test_protected_route_with_valid_token(mock_db_dependency):
    """
    Tests that a protected route can be accessed with a valid JWT.
    """
    mock_user = models.User(id=1, username="testuser", full_name="Test User")
    # Mock for get_current_user
    mock_db_dependency.query.return_value.filter.return_value.first.return_value = mock_user
    # Mock for read_users endpoint
    mock_db_dependency.query.return_value.all.return_value = [mock_user]

    token = auth.create_access_token(data={"sub": "testuser"})

    response = client.get(
        "/users",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["username"] == "testuser"

def test_expired_token():
    """
    Tests that an expired token results in 401.
    """
    token = auth.create_access_token(data={"sub": "testuser"}, expires_delta=-auth.timedelta(minutes=1))

    response = client.get(
        "/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

def test_token_user_not_found(mock_db_dependency):
    """
    Tests that a valid token for a non-existent user results in 401.
    """
    mock_db_dependency.query.return_value.filter.return_value.first.return_value = None

    token = auth.create_access_token(data={"sub": "nonexistent"})

    response = client.get(
        "/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

def test_db_check_with_valid_token(mock_db_dependency):
    """
    Tests /db-check endpoint with a valid token.
    """
    mock_user = models.User(id=1, username="testuser")
    mock_db_dependency.query.return_value.filter.return_value.first.return_value = mock_user

    mock_result = MagicMock()
    mock_result.scalar.return_value = 1
    mock_db_dependency.execute.return_value = mock_result

    token = auth.create_access_token(data={"sub": "testuser"})

    response = client.get(
        "/db-check",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "result": 1}

def test_test_endpoint_with_valid_token(mock_db_dependency):
    """
    Tests /test endpoint with a valid token.
    """
    mock_user = models.User(id=1, username="testuser")
    mock_db_dependency.query.return_value.filter.return_value.first.return_value = mock_user

    token = auth.create_access_token(data={"sub": "testuser"})

    response = client.get(
        "/test",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "test successful", "user": "testuser"}

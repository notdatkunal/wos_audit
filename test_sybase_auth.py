import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from database import get_db
import models

client = TestClient(app)

def test_login_success():
    """
    Tests successful login by mocking a successful database connection and execution.
    """
    with patch("database.create_engine") as mock_create_engine:
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        # Mocking the context manager for engine.connect()
        mock_connection = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection

        response = client.post(
            "/login",
            json={"username": "testuser", "password": "testpassword"}
        )
        assert response.status_code == 200
        assert response.json() == {"message": "Login successful", "username": "testuser"}

        # Verify that execute was called to validate connection
        assert mock_connection.execute.called
        # Verify that engine was disposed
        assert mock_engine.dispose.called

def test_login_failure():
    """
    Tests failed login by mocking a failed database connection.
    """
    with patch("database.create_engine") as mock_create_engine:
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        # Mocking connection failure
        mock_engine.connect.return_value.__enter__.side_effect = Exception("Connection failed")

        response = client.post(
            "/login",
            json={"username": "testuser", "password": "wrongpassword"}
        )
        assert response.status_code == 401
        # Should return generic error message
        assert "Authentication failed" in response.json()["detail"]
        assert "Invalid credentials" in response.json()["detail"]

        # Verify that engine was still disposed
        assert mock_engine.dispose.called

def test_read_users_mock():
    """
    Tests the /users endpoint by overriding the database dependency.
    """
    mock_db = MagicMock()
    # Create a mock user object
    mock_user = models.User(id=1, username="testuser", full_name="Test User")
    # Mocking the query results
    mock_db.query.return_value.all.return_value = [mock_user]

    # Override get_db dependency
    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.get("/users")
    assert response.status_code == 200
    # The response should match the mocked user data
    data = response.json()
    assert len(data) == 1
    assert data[0]["username"] == "testuser"
    assert data[0]["full_name"] == "Test User"

    # Clear overrides after test
    app.dependency_overrides.clear()

def test_db_check_ok():
    """
    Tests the /db-check endpoint with a successful query.
    """
    mock_db = MagicMock()
    mock_result = MagicMock()
    mock_result.scalar.return_value = 1
    mock_db.execute.return_value = mock_result

    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.get("/db-check")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "result": 1}

    app.dependency_overrides.clear()

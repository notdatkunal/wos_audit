import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from database import get_db
import models

import datetime

def test_login_success(client):
    """
    Tests successful login by mocking a successful database connection and execution,
    and also mocking the local user database query.
    """
    mock_db = MagicMock()
    mock_user = models.User(
        LoginId="testuser",
        Name="Test User",
        Id="ID1234",
        Rank="MAJOR",
        Department="ADMIN",
        DateTimeJoined=datetime.now(),
        StationCode="K"
    )
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user

    # Override get_db for this test
    app.dependency_overrides[get_db] = lambda: mock_db

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
        data = response.json()
        assert data["message"] == "Login successful"
        assert data["username"] == "testuser"
        assert "access_token" in data
        assert data["token_type"] == "bearer"

        # Verify that execute was called to validate connection
        assert mock_connection.execute.called
        # Verify that engine was disposed
        assert mock_engine.dispose.called

    app.dependency_overrides.clear()

def test_login_failure(client):
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

def test_login_user_not_in_local_db(client):
    """
    Tests successful Sybase login but user missing in application database.
    """
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None
    app.dependency_overrides[get_db] = lambda: mock_db

    with patch("database.create_engine") as mock_create_engine:
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_connection = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection

        response = client.post(
            "/login",
            json={"username": "testuser", "password": "testpassword"}
        )
        assert response.status_code == 401
        assert "not found in application database" in response.json()["detail"]

    app.dependency_overrides.clear()

def test_protected_route_no_token(client):
    """
    Verifies that protected routes return 401 when no token is provided.
    """
    response = client.get("/users")
    assert response.status_code == 401

def test_protected_route_invalid_token(client):
    """
    Verifies that protected routes return 401 with an invalid token.
    """
    response = client.get("/users", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401

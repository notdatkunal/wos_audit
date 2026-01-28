import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, timezone
from main import app
from database import get_db
import models

client = TestClient(app)

def test_forgot_password_success():
    """
    Tests /forgot-password with a valid email.
    """
    mock_db = MagicMock()
    mock_user = models.User(id=1, username="testuser", email="test@example.com")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user

    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.post("/forgot-password", json={"email": "test@example.com"})

    assert response.status_code == 200
    assert "reset_token" not in response.json()
    assert "instruction has been sent" in response.json()["message"]
    assert mock_user.reset_token is not None
    assert mock_user.reset_token_expires > datetime.now(timezone.utc).replace(tzinfo=None)
    assert mock_db.commit.called

    app.dependency_overrides.clear()

def test_forgot_password_user_not_found():
    """
    Tests /forgot-password with an invalid email should still return 200.
    """
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.post("/forgot-password", json={"email": "unknown@example.com"})

    assert response.status_code == 200
    assert "instruction has been sent" in response.json()["message"]

    app.dependency_overrides.clear()

def test_reset_password_success():
    """
    Tests /reset-password with a valid token.
    """
    mock_db = MagicMock()
    mock_user = models.User(
        id=1,
        username="testuser",
        reset_token="valid_token",
        reset_token_expires=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=1)
    )
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user

    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.post("/reset-password", json={"token": "valid_token", "new_password": "new_password123"})

    assert response.status_code == 200
    assert response.json()["message"] == "Password reset successful"
    # Verify sp_password was executed
    assert mock_db.execute.called
    # Verify token was cleared
    assert mock_user.reset_token is None
    assert mock_user.reset_token_expires is None
    assert mock_db.commit.called

    app.dependency_overrides.clear()

def test_reset_password_invalid_token():
    """
    Tests /reset-password with an invalid token.
    """
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.post("/reset-password", json={"token": "invalid_token", "new_password": "new_password123"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid token"

    app.dependency_overrides.clear()

def test_reset_password_expired_token():
    """
    Tests /reset-password with an expired token.
    """
    mock_db = MagicMock()
    mock_user = models.User(
        id=1,
        username="testuser",
        reset_token="expired_token",
        reset_token_expires=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=1)
    )
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user

    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.post("/reset-password", json={"token": "expired_token", "new_password": "new_password123"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Token expired"

    app.dependency_overrides.clear()

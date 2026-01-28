import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, timezone
from main import app
from database import get_db, get_reset_db
import models, reset_models

client = TestClient(app)

def test_set_user_email_success():
    """
    Tests /set-user-email with a valid user and password.
    """
    mock_reset_db = MagicMock()
    mock_reset_db.query.return_value.filter.return_value.first.return_value = None

    app.dependency_overrides[get_reset_db] = lambda: mock_reset_db

    with patch("database.create_engine") as mock_create_engine:
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_connection = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection

        response = client.post(
            "/set-user-email",
            json={"username": "testuser", "password": "testpassword", "email": "test@example.com"}
        )

        assert response.status_code == 200
        assert response.json()["message"] == "Email test@example.com linked to user testuser"
        assert mock_reset_db.add.called
        assert mock_reset_db.commit.called

    app.dependency_overrides.clear()

def test_set_user_email_failure():
    """
    Tests /set-user-email with invalid password.
    """
    mock_reset_db = MagicMock()
    app.dependency_overrides[get_reset_db] = lambda: mock_reset_db

    with patch("database.create_engine") as mock_create_engine:
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_engine.connect.return_value.__enter__.side_effect = Exception("Auth failed")

        response = client.post(
            "/set-user-email",
            json={"username": "testuser", "password": "wrongpassword", "email": "test@example.com"}
        )

        assert response.status_code == 401
        assert "Authentication failed" in response.json()["detail"]

    app.dependency_overrides.clear()

def test_forgot_password_success():
    """
    Tests /forgot-password with a linked email.
    """
    mock_reset_db = MagicMock()
    mock_mapping = reset_models.UserEmail(id=1, username="testuser", email="test@example.com")
    mock_reset_db.query.return_value.filter.return_value.first.return_value = mock_mapping

    app.dependency_overrides[get_reset_db] = lambda: mock_reset_db

    response = client.post("/forgot-password", json={"email": "test@example.com"})

    assert response.status_code == 200
    assert "instruction has been sent" in response.json()["message"]
    # Verify info was added to reset_db
    assert mock_reset_db.add.called
    assert mock_reset_db.commit.called

    app.dependency_overrides.clear()

def test_forgot_password_email_not_linked():
    """
    Tests /forgot-password with an unlinked email should still return 200.
    """
    mock_reset_db = MagicMock()
    mock_reset_db.query.return_value.filter.return_value.first.return_value = None

    app.dependency_overrides[get_reset_db] = lambda: mock_reset_db

    response = client.post("/forgot-password", json={"email": "unknown@example.com"})

    assert response.status_code == 200
    assert "instruction has been sent" in response.json()["message"]
    assert not mock_reset_db.add.called

    app.dependency_overrides.clear()

def test_reset_password_success():
    """
    Tests /reset-password with a valid token.
    """
    mock_db = MagicMock()
    mock_reset_db = MagicMock()
    mock_reset_info = reset_models.PasswordReset(
        id=1,
        username="testuser",
        token="valid_token",
        expires_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=1)
    )
    mock_reset_db.query.return_value.filter.return_value.first.return_value = mock_reset_info

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_reset_db] = lambda: mock_reset_db

    response = client.post("/reset-password", json={"token": "valid_token", "new_password": "new_password123"})

    assert response.status_code == 200
    assert response.json()["message"] == "Password reset successful"
    # Verify sp_password was executed on Sybase
    assert mock_db.execute.called
    # Verify token was cleared from SQLite
    assert mock_reset_db.delete.called
    assert mock_reset_db.commit.called

    app.dependency_overrides.clear()

def test_reset_password_invalid_token():
    """
    Tests /reset-password with an invalid token.
    """
    mock_db = MagicMock()
    mock_reset_db = MagicMock()
    mock_reset_db.query.return_value.filter.return_value.first.return_value = None

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_reset_db] = lambda: mock_reset_db

    response = client.post("/reset-password", json={"token": "invalid_token", "new_password": "new_password123"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid token"

    app.dependency_overrides.clear()

def test_reset_password_expired_token():
    """
    Tests /reset-password with an expired token.
    """
    mock_db = MagicMock()
    mock_reset_db = MagicMock()
    mock_reset_info = reset_models.PasswordReset(
        id=1,
        username="testuser",
        token="expired_token",
        expires_at=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=1)
    )
    mock_reset_db.query.return_value.filter.return_value.first.return_value = mock_reset_info

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_reset_db] = lambda: mock_reset_db

    response = client.post("/reset-password", json={"token": "expired_token", "new_password": "new_password123"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Token expired"
    # Verify token was deleted
    assert mock_reset_db.delete.called

    app.dependency_overrides.clear()

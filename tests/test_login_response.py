import pytest
from fastapi.testclient import TestClient
from main import app
from database import get_db, get_reset_db
from models import User, UserRole
from unittest.mock import MagicMock, patch
from sqlalchemy import text


def test_login_returns_name(client):
    with patch("database.get_user_engine") as mock_get_engine:
        # Mock engine and connection
        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_get_engine.return_value = mock_engine
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = MagicMock()

        # Mock DB session
        mock_db = MagicMock()
        
        # Mock user object (string attributes required for LoginResponse validation)
        mock_user = MagicMock()
        mock_user.LoginId = "user1"
        mock_user.Name = "Sarah Brown"
        mock_user.StationCode = "K"
        mock_user.Rank = "MAJOR"
        mock_user.Department = "ADMIN"

        mock_role = MagicMock()
        mock_role.RoleName = "AUDITOR"
        mock_user.roles = [mock_role]
        
        # Setup query filter chain
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        # Override dependencies
        app.dependency_overrides[get_db] = lambda: mock_db

        login_data = {"username": "user1", "password": "password"}
        response = client.post("/login", json=login_data)

        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert data["name"] == "Sarah Brown"
        assert data["username"] == "user1"
        assert "AUDITOR" in data["roles"]
        assert "access_token" in data

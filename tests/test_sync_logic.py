import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from sqlalchemy import text
from datetime import datetime
from main import app, sync_db_users
from database import get_db
import models

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_sync_db_users():
    """
    Tests the sync_db_users function by mocking the database queries.
    """
    mock_db = MagicMock()
    mock_engine = MagicMock()
    mock_conn = MagicMock()
    
    mock_db.get_bind.return_value = mock_engine
    # Mocking engine.connect().execution_options(...).__enter__()
    mock_engine.connect.return_value.execution_options.return_value.__enter__.return_value = mock_conn

    # Mock Users table search result
    mock_user = models.User(
        LoginId="user123",
        Name="Test User",
        Id="ID1234",
        Rank="MAJOR",
        Department="ADMIN",
        DateTimeJoined=datetime.now(),
        StationCode="K"
    )
    mock_db.query.return_value.all.return_value = [mock_user]
    
    # Mock Sybase login check
    def db_execute_mock(query, params=None):
        query_str = str(query)
        mock_result = MagicMock()
        if "syslogins" in query_str:
            mock_result.fetchone.return_value = None # Login does not exist
        elif "sysusers" in query_str:
            mock_result.fetchone.return_value = None # User does not exist
        return mock_result

    mock_conn.execute.side_effect = db_execute_mock

    # Run the sync function
    sync_db_users(mock_db)

    # Verify that sp_addlogin and sp_adduser were called on the connection
    calls = [call[0][0].text if hasattr(call[0][0], 'text') else str(call[0][0]) for call in mock_conn.execute.call_args_list]
    
    addlogin_called = any("sp_addlogin" in c for c in calls)
    adduser_called = any("sp_adduser" in c for c in calls)
    
    assert addlogin_called, "sp_addlogin should have been called"
    assert adduser_called, "sp_adduser should have been called"

def test_login_api_integration(client):
    """
    Tests the login API with the new synchronization logic implicitly (through mocking).
    """
    mock_db = MagicMock()
    # Mock user in application database
    mock_user = models.User(
        LoginId="testuser",
        Name="Test User",
        Id="ID1234",
        Rank="MAJOR",
        Department="ADMIN",
        DateTimeJoined=datetime.now(),
        StationCode="K",
        roles=[]
    )
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    
    app.dependency_overrides[get_db] = lambda: mock_db

    with patch("database.get_user_engine") as mock_get_engine:
        mock_engine = MagicMock()
        mock_get_engine.return_value = mock_engine
        mock_connection = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        
        # Test the login endpoint
        response = client.post(
            "/login",
            json={"username": "testuser", "password": "password"}
        )
        
        assert response.status_code == 200
        assert response.json()["username"] == "testuser"
        assert "access_token" in response.json()

    app.dependency_overrides.clear()

import pytest
from fastapi.testclient import TestClient
from main import app
from database import get_db
from unittest.mock import MagicMock
import schemas
import models

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

def test_update_wosline_vetted_qty(client, mock_db_dependency):
    # Mock data
    wos_serial = 101
    line_serial = 1
    new_vetted_qty = 50.0

    # Mocking the line object
    mock_line = MagicMock()
    mock_line.WOSSerial = wos_serial
    mock_line.WOSLineSerial = line_serial
    mock_line.VettedQty = 10.0
    mock_line.ItemCode = "ITEM001"
    mock_line.ItemDesc = "Test Item"
    mock_line.ItemDeno = "EA"
    mock_line.SOS = "SOS"
    mock_line.AuthorisedQty = 100.0
    mock_line.AuthorityRef = "REF001"
    mock_line.AuthorityDate = "2023-01-01T00:00:00"
    mock_line.Justification = "Justification"

    # Mock the query
    mock_query = mock_db_dependency.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = mock_line

    # Request body
    update_data = {"VettedQty": new_vetted_qty}

    response = client.put(f"/wosline/{wos_serial}/{line_serial}", json=update_data)

    # Assertions
    assert response.status_code == 200
    assert mock_line.VettedQty == new_vetted_qty
    assert mock_db_dependency.commit.called
    assert mock_db_dependency.refresh.called

def test_update_wosline_not_found(client, mock_db_dependency):
    # Mock the query to return None
    mock_query = mock_db_dependency.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = None

    response = client.put("/wosline/999/999", json={"VettedQty": 10.0})

    assert response.status_code == 404
    assert response.json()["detail"] == "WOSLine not found"

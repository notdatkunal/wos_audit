import pytest
from fastapi.testclient import TestClient
from main import app
from database import get_db
from unittest.mock import MagicMock
from datetime import datetime

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

def test_get_correspondence(client, mock_db_dependency):
    # Setup mock data
    mock_correspondence = MagicMock()
    mock_correspondence.LineNo = 1
    mock_correspondence.TableName = "WOSMaster"
    mock_correspondence.PrimaryKeyValue = "24"
    mock_correspondence.RoleName = "LOGO"
    mock_correspondence.CorrespondenceBy = "t2533104"
    mock_correspondence.CorrespondenceToRole = "NLAO"
    mock_correspondence.DateTimeCorrespondence = datetime(2025, 12, 22, 15, 44, 7)
    mock_correspondence.CorrespondenceType = "Fwded"
    mock_correspondence.StationCode = "K"
    mock_correspondence.Remarks = "WOS forwarded by LOGO to NLAO"
    mock_correspondence.DocumentType = "NOTE"
    mock_correspondence.CorrespondenceChoice = "Y"
    
    mock_db_dependency.query.return_value.outerjoin.return_value.filter.return_value.all.return_value = [(mock_correspondence, "Forwarded")]
    
    response = client.get("/correspondence/24")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["LineNo"] == 1
    assert data[0]["PrimaryKeyValue"] == "24"
    assert data[0]["TableName"] == "WOSMaster"
    assert data[0]["CorrespondenceType"] == "Fwded"
    assert data[0]["CorrespondenceTypeDescription"] == "Forwarded"



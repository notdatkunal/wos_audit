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

def test_get_wos_masters(client, mock_db_dependency):
    # Setup mock data for WOSMaster (optional string fields must be None or str for response validation)
    mock_master = MagicMock()
    mock_master.WOSSerial = 1
    mock_master.CustomerCode = "C001"
    mock_master.WOSType = "TYP"
    mock_master.InitiatedBy = "user1"
    mock_master.DateTimeInitiated = datetime(2026, 1, 31, 12, 0, 0)
    mock_master.Remarks = "Test Remark"
    mock_master.ConcurredBy = None
    mock_master.DateTimeConcurred = None
    mock_master.WONumber = None
    mock_master.WOIDate = None
    mock_master.ApprovedBy = None
    mock_master.DateTimeApproved = None
    mock_master.SanctionNo = None
    mock_master.SanctionDate = None
    mock_master.ClosedBy = None
    mock_master.DateTimeClosed = None

    # Mocking the __table__.columns for the dict conversion
    col1 = MagicMock(); col1.name = "WOSSerial"; setattr(mock_master, "WOSSerial", 1)
    col2 = MagicMock(); col2.name = "CustomerCode"; setattr(mock_master, "CustomerCode", "C001")
    col3 = MagicMock(); col3.name = "WOSType"; setattr(mock_master, "WOSType", "TYP")
    col4 = MagicMock(); col4.name = "InitiatedBy"; setattr(mock_master, "InitiatedBy", "user1")
    col5 = MagicMock(); col5.name = "DateTimeInitiated"; setattr(mock_master, "DateTimeInitiated", datetime(2026, 1, 31, 12, 0, 0))
    col6 = MagicMock(); col6.name = "Remarks"; setattr(mock_master, "Remarks", "Test Remark")
    
    # List of common fields to avoid missing attributes
    fields = [
        "WOSSerial", "CustomerCode", "WOSType", "InitiatedBy", "DateTimeInitiated",
        "ConcurredBy", "DateTimeConcurred", "WONumber", "WOIDate", "ApprovedBy",
        "DateTimeApproved", "SanctionNo", "SanctionDate", "ClosedBy", "DateTimeClosed", "Remarks"
    ]
    
    mock_columns = []
    for field in fields:
        col = MagicMock()
        col.name = field
        mock_columns.append(col)
    # Use setattr because __table__ is a protected name in MagicMock
    mock_table = MagicMock()
    mock_table.columns = mock_columns
    setattr(mock_master, "__table__", mock_table)
    
    mock_db_dependency.query.return_value.outerjoin.return_value.all.return_value = [(mock_master, "Type Description")]
    
    response = client.get("/wosmaster")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["WOSSerial"] == 1
    assert data[0]["WOSType"] == "TYP"
    assert data[0]["WOSTypeDescription"] == "Type Description"

def test_get_single_wos_master(client, mock_db_dependency):
    # Setup mock data for WOSMaster (optional string fields must be None or str for response validation)
    mock_master = MagicMock()
    mock_master.WOSSerial = 1
    mock_master.CustomerCode = "C001"
    mock_master.WOSType = "TYP"
    mock_master.InitiatedBy = "user1"
    mock_master.DateTimeInitiated = datetime(2026, 1, 31, 12, 0, 0)
    mock_master.Remarks = "Test Remark"
    mock_master.ConcurredBy = None
    mock_master.DateTimeConcurred = None
    mock_master.WONumber = None
    mock_master.WOIDate = None
    mock_master.ApprovedBy = None
    mock_master.DateTimeApproved = None
    mock_master.SanctionNo = None
    mock_master.SanctionDate = None
    mock_master.ClosedBy = None
    mock_master.DateTimeClosed = None

    fields = [
        "WOSSerial", "CustomerCode", "WOSType", "InitiatedBy", "DateTimeInitiated",
        "ConcurredBy", "DateTimeConcurred", "WONumber", "WOIDate", "ApprovedBy",
        "DateTimeApproved", "SanctionNo", "SanctionDate", "ClosedBy", "DateTimeClosed", "Remarks"
    ]
    
    mock_columns = []
    for field in fields:
        col = MagicMock()
        col.name = field
        mock_columns.append(col)
    # Use setattr because __table__ is a protected name in MagicMock
    mock_table = MagicMock()
    mock_table.columns = mock_columns
    setattr(mock_master, "__table__", mock_table)
    
    mock_db_dependency.query.return_value.outerjoin.return_value.filter.return_value.first.return_value = (mock_master, "Type Description")
    
    response = client.get("/wosmaster/1")
    
    assert response.status_code == 200
    data = response.json()
    assert data["WOSSerial"] == 1
    assert data["WOSTypeDescription"] == "Type Description"

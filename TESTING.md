# Testing Guide

This document provides a comprehensive overview of the testing suites for the `wos_audit` application, including how to set up, execute, and troubleshoot tests.

## Test Framework

The project uses:
- **pytest**: The primary test runner.
- **httpx**: Used by FastAPI's `TestClient` for simulating HTTP requests.
- **unittest.mock**: Extensive use of mocking to isolate components from the Sybase database.

## Prerequisites

Ensure all dependencies are installed:

```bash
pip install -r requirements.txt
```

## Running Tests

### Run All Tests

To run all available tests:

```bash
pytest
```

### Run Specific Test Suites

You can run individual test files based on the functionality you are testing:

- **JWT Authentication**: `pytest test_jwt_auth.py`
- **Forgot Password flow**: `pytest test_forgot_password.py`
- **Sybase Auth Simulation**: `pytest test_sybase_auth.py`
- **Login Response Structure**: `pytest test_login_response.py`
- **Database Sync Logic**: `pytest test_sync_logic.py`
- **General API Endpoints**: `pytest test_main.py`

### Useful Pytest Flags

- `-v`: Verbose output.
- `-s`: Allow print statements to show in the console (useful for debugging).
- `--cov=.`: If `pytest-cov` is installed, generates a coverage report.

---

## Test Inventory

| File | Category | Description |
| :--- | :--- | :--- |
| `test_jwt_auth.py` | Auth | Validates JWT token generation, expiration, and protected route access. |
| `test_forgot_password.py` | Account | Tests the "Forgot Password" email flow and token-based reset functionality. |
| `test_sybase_auth.py` | Integration | Mocks Sybase calls to verify the logic of authenticating against the legacy DB. |
| `test_sync_logic.py` | Data | Verifies logic for syncing users or roles between databases. |
| `test_login_response.py` | API | Specifically checks the structure of the JSON returned during login. |
| `test_connection.py` | Diagnostic | **Manual check**: Run `python test_connection.py` to verify ODBC driver connectivity. |

---

## Environment & Mocking

### The `.env` File
Most tests use mocked database connections. However, `test_connection.py` and some integration tests may require a valid `.env` file with proper Sybase credentials. Use `.env.example` as a template.

### Mocking Strategy
The application uses FastAPI's `dependency_overrides` heavily. In most tests, the `get_db` and `get_reset_db` dependencies are replaced with `MagicMock` objects to simulate database interactions without requiring a live Sybase instance.

Example of dependency override in tests:
```python
from main import app
from database import get_db
from unittest.mock import MagicMock

def test_something():
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    # ... test logic ...
    app.dependency_overrides.clear()
```

## Troubleshooting

- **ODBC Errors**: If `test_connection.py` fails, check your `DB_DRIVER` in `.env`. Common drivers include `{Adaptive Server Enterprise}` or `{SAP ASE ODBC Driver}`.
- **SQLite Missing**: The password reset flow uses a local SQLite database (`password_reset.db`). Ensure the directory is writable.
- **Import Errors**: Ensure you are running pytest from the project root so that `main.py` and other modules are in the path.

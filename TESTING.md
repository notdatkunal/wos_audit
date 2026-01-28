# Testing Guide

This document describes how to run tests for the `wos_audit` application.

## Test Framework

The project uses `pytest` as its testing framework and `httpx` (required by FastAPI's `TestClient`) for making requests to the application.

## Running Tests

To run all tests in the project, use the following command from the root directory:

```bash
pytest
```

### Running Specific Tests

To run tests in a specific file:

```bash
pytest test_main.py
```

To run a specific test function within a file:

```bash
pytest test_main.py::test_read_test_endpoint
```

### Running with Coverage (Optional)

If you have `pytest-cov` installed, you can run tests with coverage reporting:

```bash
pytest --cov=.
```

## Adding New Tests

When adding new features or fixing bugs, please ensure that you add corresponding tests in the `test_main.py` file or create new test files prefixed with `test_`.

A typical test case using FastAPI's `TestClient` looks like this:

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_new_feature():
    response = client.get("/new-feature")
    assert response.status_code == 200
    assert response.json() == {"message": "success"}
```

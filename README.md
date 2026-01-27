# wos_audit

`wos_audit` is a FastAPI backend for the audit application of the Warrant of Stores (WOS) application for Material Organisation Mumbai.

## Project Info

This application serves as the backend for auditing Warrant of Stores (WOS) processes within the Material Organisation in Mumbai. It provides endpoints for testing and auditing functionalities.

## Prerequisites

- Python 3.7+
- pip (Python package installer)

## Installation

1. Clone the repository.
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running the App

### Using the run script

You can use the provided `run_app.sh` script to start the application on port 8089 in the background.

```bash
chmod +x run_app.sh
./run_app.sh
```

The logs will be available in `app.log`.

### Using Uvicorn Directly

Alternatively, you can start the application using `uvicorn` directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 8089
```

## Testing

To run the tests for this application, you can use `pytest`. For more detailed instructions, please refer to [TESTING.md](TESTING.md).

```bash
pytest
```

## Contributing

If you would like to contribute to this project, please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

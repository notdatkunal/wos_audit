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

## Docker Setup (Full Stack)

The easiest way to run the entire stack (FastAPI app + Sybase database) is using Docker Compose.

1.  **Configure Environment**: Ensure your `.env` file exists with the necessary secrets.
2.  **Start the stack**:
    ```bash
    docker compose up --build -d
    ```
3.  **Check logs**:
    ```bash
    docker compose logs -f app
    ```

The application will be available at `http://localhost:8089`.

## Database Setup (Sybase Only)

If you prefer to run only the database in Docker and the app locally:

1.  **Start the Sybase container**:
    ```bash
    docker compose up -d sybase sybase-setup
    ```
2.  **Wait for initialization**: The `sybase-setup` container will automatically run `init_db.sql`.

### Environment Variables

Ensure your `.env` file is configured to match your environment:

```env
SYBASE_SERVER=localhost
SYBASE_PORT=5000
SYBASE_DB=auditdb
MAIN_DB_USER=sa
MAIN_DB_PASS=password
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Optional: override DB driver and TDS version (useful for FreeTDS)
# DB_DRIVER={Adaptive Server Enterprise}
# TDS_VERSION=5.0
```

## Contributing

If you would like to contribute to this project, please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

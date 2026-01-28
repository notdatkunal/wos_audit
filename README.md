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

## Database Setup (Sybase)

This project uses Sybase ASE. For development, you can run Sybase in a Docker container.

### Using Docker Compose

1. Start the Sybase container:

```bash
docker-compose up -d
```

2. Wait for the container to be healthy. You can check the status with `docker-compose ps`.

3. Initialize the database schema:

```bash
docker exec -i sybase_audit /sybase/OCS-15_0/bin/isql -S SYBASE -U sa -P password < init_db.sql
```

### Environment Variables

Ensure your `.env` file is configured to match your Sybase instance:

```env
SYBASE_SERVER=localhost
SYBASE_PORT=5000
SYBASE_DB=master
MAIN_DB_USER=sa
MAIN_DB_PASS=password
```

## Contributing

If you would like to contribute to this project, please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

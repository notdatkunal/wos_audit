from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
import database, models, schemas

app = FastAPI()

@app.get("/test")
async def test_endpoint():
    """
    Existing test endpoint.
    """
    return {"message": "test successful"}

@app.post("/login", response_model=schemas.LoginResponse)
async def login(request: schemas.LoginRequest):
    """
    Authenticates a user by attempting a connection to the Sybase database
    using their credentials.
    """
    # Create a temporary engine with the user's credentials
    engine = database.get_user_engine(request.username, request.password)
    try:
        # Attempt to establish a connection and execute a simple query
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            # A successful connection and execution implies valid credentials
            return {"message": "Login successful", "username": request.username}
    except Exception:
        # Connection failure indicates invalid credentials or network issues
        # Generic error message to avoid information leakage
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed: Invalid credentials or database unavailable"
        )
    finally:
        # Dispose of the temporary engine to prevent resource leaks
        engine.dispose()

@app.get("/users", response_model=list[schemas.User])
def read_users(db: Session = Depends(database.get_db)):
    """
    Retrieves all users using the global 'main' user session.
    """
    users = db.query(models.User).all()
    return users

@app.get("/db-check")
def db_check(db: Session = Depends(database.get_db)):
    """
    Checks the database connectivity using the global 'main' user session.
    """
    try:
        # Simple query to verify connectivity
        result = db.execute(text("SELECT 1"))
        return {"status": "ok", "result": result.scalar()}
    except Exception as e:
        # For internal diagnostics, we might log the error,
        # but here we return it for the test/demo purpose
        return {"status": "error", "detail": str(e)}

import secrets
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
import database, models, schemas

app = FastAPI()

# @app.on_event("startup")
# def startup():
#     """
#     Creates the database tables on startup.
#     """
#     database.Base.metadata.create_all(bind=database.engine)

@app.get("/test")
@app.get("/test2")
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

@app.post("/forgot-password")
async def forgot_password(request: schemas.ForgotPasswordRequest, db: Session = Depends(database.get_db)):
    """
    Initiates the password reset process by generating a token.
    Returns a generic message to prevent email enumeration.
    """
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if user:
        # Generate token
        token = secrets.token_urlsafe(32)
        user.reset_token = token
        # Using timezone-aware UTC datetime but storing as naive for DB compatibility if needed
        user.reset_token_expires = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=1)
        db.commit()
        # In a real application, we would send an email here.
        # For simulation purposes, the token is generated and stored in the database.

    return {"message": "If the email exists, a password reset instruction has been sent."}

@app.post("/reset-password")
async def reset_password(request: schemas.ResetPasswordRequest, db: Session = Depends(database.get_db)):
    """
    Resets the user's password using a valid token.
    """
    user = db.query(models.User).filter(models.User.reset_token == request.token).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

    # Compare with naive UTC now
    if user.reset_token_expires < datetime.now(timezone.utc).replace(tzinfo=None):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token expired")

    # Reset password in Sybase using the 'main' user session
    try:
        # Sybase sp_password: old_password, new_password, login_name
        # Since we are resetting, we use NULL for old_password (requires sa/admin privileges)
        db.execute(text("EXEC sp_password NULL, :new_password, :username"),
                   {"new_password": request.new_password, "username": user.username})
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset password in database: {str(e)}"
        )

    # Clear token
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()

    return {"message": "Password reset successful"}

import secrets
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

import database, models, schemas, auth, reset_models


app = FastAPI()

@app.on_event("startup")
def startup_event():
    # Create tables in Sybase if they do not exist
    models.Base.metadata.create_all(bind=database.get_main_engine())

@app.get("/test")
async def test_endpoint(current_user: models.User = Depends(auth.get_current_user)):

    """
    Existing test endpoint, now protected.
    """
    return {"message": "test successful", "user": current_user.username}

@app.post("/login", response_model=schemas.LoginResponse)
async def login(request: schemas.LoginRequest, db: Session = Depends(database.get_db)):
    """
    Authenticates a user by attempting a connection to the Sybase database
    using their credentials, then issues a JWT.
    """
    # Create a temporary engine with the user's credentials
    engine = database.get_user_engine(request.username, request.password)
    try:
        # Attempt to establish a connection and execute a simple query
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            # A successful connection and execution implies valid credentials

            # Fetch user from local DB to include in token or just verify existence
            user = db.query(models.User).filter(models.User.username == request.username).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User authenticated with DB but not found in application database"
                )

            access_token = auth.create_access_token(
                data={"sub": user.username, "roles": [r.role_name for r in user.roles]}
            )
            return {
                "message": "Login successful",
                "username": request.username,
                "access_token": access_token,
                "token_type": "bearer"
            }
    except HTTPException:
        raise
    except Exception:
        # Connection failure indicates invalid credentials or network issues
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed: Invalid credentials or database unavailable"
        )
    finally:
        # Dispose of the temporary engine to prevent resource leaks
        engine.dispose()

@app.get("/users", response_model=list[schemas.User])
def read_users(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Retrieves all users using the global 'main' user session.
    Protected by JWT.
    """
    users = db.query(models.User).all()
    return users

@app.get("/db-check")
def db_check(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Checks the database connectivity using the global 'main' user session.
    Protected by JWT.
    """
    try:
        # Simple query to verify connectivity
        result = db.execute(text("SELECT 1"))
        return {"status": "ok", "result": result.scalar()}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.post("/set-user-email")
async def set_user_email(
    request: schemas.LinkEmailRequest,
    reset_db: Session = Depends(database.get_reset_db)
):
    """
    Links a username (from Sybase) to an email address in SQLite.
    Requires the user's current password for authentication.
    """
    # Authenticate user by attempting a connection to Sybase
    engine = database.get_user_engine(request.username, request.password)
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed: Invalid credentials"
        )
    finally:
        engine.dispose()

    # Update or create the mapping in SQLite
    mapping = reset_db.query(reset_models.UserEmail).filter(
        reset_models.UserEmail.username == request.username
    ).first()

    if mapping:
        mapping.email = request.email
    else:
        mapping = reset_models.UserEmail(username=request.username, email=request.email)
        reset_db.add(mapping)

    reset_db.commit()
    return {"message": f"Email {request.email} linked to user {request.username}"}

@app.post("/forgot-password")
async def forgot_password(
    request: schemas.ForgotPasswordRequest,
    reset_db: Session = Depends(database.get_reset_db)
):
    """
    Initiates the password reset process by generating a token.
    Uses the SQLite mapping to find the username associated with the email.
    Returns a generic message to prevent email enumeration.
    """
    # Find the username associated with this email in SQLite
    mapping = reset_db.query(reset_models.UserEmail).filter(
        reset_models.UserEmail.email == request.email
    ).first()

    if mapping:
        # Generate token
        token = secrets.token_urlsafe(32)
        # Store in SQLite
        reset_info = reset_models.PasswordReset(
            username=mapping.username,
            token=token,
            expires_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=1)
        )
        reset_db.add(reset_info)
        reset_db.commit()
        # In a real application, we would send an email with the token here.
        # DEBUG: print(f"DEBUG: Reset token for {mapping.username}: {token}")

    return {"message": "If the email exists, a password reset instruction has been sent."}

@app.post("/reset-password")
async def reset_password(
    request: schemas.ResetPasswordRequest,
    db: Session = Depends(database.get_db),
    reset_db: Session = Depends(database.get_reset_db)
):
    """
    Resets the user's password using a valid token from SQLite.
    """
    reset_info = reset_db.query(reset_models.PasswordReset).filter(
        reset_models.PasswordReset.token == request.token
    ).first()

    if not reset_info:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

    if reset_info.expires_at < datetime.now(timezone.utc).replace(tzinfo=None):
        reset_db.delete(reset_info)
        reset_db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token expired")

    # Reset password in Sybase
    try:
        db.execute(text("EXEC sp_password NULL, :new_password, :username"),
                   {"new_password": request.new_password, "username": reset_info.username})
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset password in database: {str(e)}"
        )

    # Clear token from SQLite
    reset_db.delete(reset_info)
    reset_db.commit()

    return {"message": "Password reset successful"}

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
import database, models, schemas, auth

app = FastAPI()

@app.get("/test")
@app.get("/test2")
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

import secrets
import random
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

import database, models, schemas, auth, reset_models


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    # Create tables in Sybase if they do not exist
    models.Base.metadata.create_all(bind=database.get_main_engine())

    # Check length of the users table and seed if empty
    SessionLocal = database.get_session_local()
    db = SessionLocal()
    try:
        user_count = db.query(models.User).count()
        if user_count == 0:
            seed_users(db)
        
        # Ensure all usernames in Users table exist as db users
        sync_db_users(db)
    except Exception as e:
        print(f"Error during startup synchronization: {e}")
    finally:
        db.close()

def sync_db_users(db: Session):
    """
    Ensures all users in the 'Users' table exist as Sybase database logins and users.
    Default password for new users is 'password'.
    Executed outside of a transaction as sp_addlogin/sp_adduser require it.
    """
    try:
        users = db.query(models.User).all()
        # Use a raw connection with autocommit for system stored procedures
        engine = db.get_bind()
        
        for user in users:
            username = user.LoginId
            
            with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
                # Check if login exists in Sybase
                login_exists = conn.execute(
                    text("SELECT name FROM master..syslogins WHERE name = :username"),
                    {"username": username}
                ).fetchone()

                if not login_exists:
                    print(f"Login {username} not found. Creating Sybase login...")
                    # sp_addlogin creates a server-wide login
                    conn.execute(
                        text("EXEC sp_addlogin :username, 'password', :dbname"),
                        {"username": username, "dbname": database.SYBASE_DB}
                    )
                
                # Check if user exists in the current database
                user_exists = conn.execute(
                    text("SELECT name FROM sysusers WHERE name = :username"),
                    {"username": username}
                ).fetchone()

                if not user_exists:
                    print(f"User {username} not found in database {database.SYBASE_DB}. Adding user...")
                    # sp_adduser adds the login as a user to the current database
                    conn.execute(
                        text("EXEC sp_adduser :username"),
                        {"username": username}
                    )
    except Exception as e:
        print(f"Critical error during Sybase user sync: {e}")

def seed_users(db: Session):
    """
    Seeds the database with 3 random users and their roles if the users table is empty.
    Stores the insert queries into 'seed_users.sql'.
    """
    first_names = ["John", "Jane", "Robert", "Emily", "Michael", "Sarah", "David", "Linda"]
    last_names = ["Smith", "Doe", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis"]
    ranks = ["MAJOR", "CAPTAIN", "LT COL", "COLONEL"]
    depts = ["ADMIN", "LOG", "OPS", "TECH"]
    stations = ['K', 'U', 'B', 'V', 'D', 'P', 'A', 'G']
    # Role names must be in ALL CAPS
    roles_pool = ["NLAO", "AUDITOR", ]
    
    sql_queries = []
    
    for i in range(3):
        # Generate random user data
        login_id = f"user{i+1}"
        user_id = f"ID{random.randint(1000, 9999)}"
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        rank = random.choice(ranks)
        dept = random.choice(depts)
        stn = random.choice(stations)
        
        joined_date = datetime.now() - timedelta(days=random.randint(100, 1000))
        
        new_user = models.User(
            LoginId=login_id,
            Id=user_id,
            Name=name,
            Rank=rank,
            Department=dept,
            DateTimeJoined=joined_date,
            StationCode=stn
        )
        db.add(new_user)
        
        # Build SQL query string
        sql_queries.append(
            f"INSERT INTO Users (LoginId, Id, Name, Rank, Department, DateTimeJoined, StationCode) "
            f"VALUES ('{login_id}', '{user_id}', '{name}', '{rank}', '{dept}', '{joined_date.strftime('%Y-%m-%d %H:%M:%S')}', '{stn}');"
        )
        
        # Seed user roles (one-to-many)
        num_roles = random.randint(1, 3)
        assigned_roles = random.sample(roles_pool, num_roles)
        
        for role_name in assigned_roles:
            activated_date = joined_date + timedelta(days=1)
            new_role = models.UserRole(
                LoginId=login_id,
                RoleName=role_name,
                DateTimeActivated=activated_date,
                StationCode=stn
            )
            db.add(new_role)
            
            sql_queries.append(
                f"INSERT INTO UserRole (LoginId, RoleName, DateTimeActivated, StationCode) "
                f"VALUES ('{login_id}', '{role_name}', '{activated_date.strftime('%Y-%m-%d %H:%M:%S')}', '{stn}');"
            )
            
    db.commit()
    
    # Store queries in seed_users.sql
    with open("seed_users.sql", "w") as f:
        f.write("\n".join(sql_queries))
    
    print(f"Successfully seeded 3 users and roles. Queries saved to seed_users.sql")

@app.get("/test")
def test_endpoint(db: Session = Depends(database.get_db)):
    """
    Test endpoint to verify database connectivity.
    """
    try:
        result = db.execute(text("SELECT 1"))
        return {"message": "test successful", "db_result": result.scalar()}
    except Exception as e:
        return {"message": "test failed", "error": str(e)}

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
            user = db.query(models.User).filter(models.User.LoginId == request.username).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User authenticated with DB but not found in application database"
                )

            user_roles = [r.RoleName for r in user.roles]
            access_token = auth.create_access_token(
                data={"sub": user.LoginId, "roles": user_roles}
            )
            return {
                "message": "Login successful",
                "username": request.username,
                "name": user.Name,
                "stationCode": user.StationCode,
                "rank": user.Rank,
                "department": user.Department,
                "roles": user_roles,
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
    db: Session = Depends(database.get_db)
):
    """
    Checks the database connectivity using the global 'main' user session.
    """
    try:
        # Simple query to verify connectivity
        result = db.execute(text("SELECT 1"))
        return {"status": "ok", "result": result.scalar()}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.get("/codetable", response_model=list[schemas.CodeTable])
def get_codetable_data(column_name: str, db: Session = Depends(database.get_db)):
    """
    Returns all data from CodeTable for a given ColumnName.
    """
    return db.query(models.CodeTable).filter(models.CodeTable.ColumnName == column_name).all()

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

"""
API layer: FastAPI routes that delegate to services and map exceptions to HTTP responses.
"""

import os
from typing import Optional, List
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

import database
import models
import schemas
import auth
from repositories import get_user_count, seed_users, sync_db_users, run_test_query
from services import (
    get_all_users as svc_get_all_users,
    get_wos_masters as svc_get_wos_masters,
    get_wos_master_by_serial as svc_get_wos_master,
    get_wos_lines as svc_get_wos_lines,
    get_wos_line as svc_get_wos_line,
    update_wos_line as svc_update_wos_line,
    bulk_update_wos_lines as svc_bulk_update_wos_lines,
    get_correspondence as svc_get_correspondence,
    get_codetable_data as svc_get_codetable_data,
    login_user as svc_login_user,
    forgot_password as svc_forgot_password,
    reset_password as svc_reset_password,
)
from exceptions import DatabaseError, NotFoundError
from models import VettedQtyValidationError


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---- Exception handlers: map domain exceptions to HTTP ----
@app.exception_handler(NotFoundError)
def handle_not_found(request, exc: NotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


@app.exception_handler(DatabaseError)
def handle_database_error(request, exc: DatabaseError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": exc.message or "Database error"},
    )


@app.exception_handler(VettedQtyValidationError)
def handle_vetted_qty_validation(request, exc: VettedQtyValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


@app.on_event("startup")
def startup_event():
    if os.getenv("TESTING") == "true":
        print("Skipping startup synchronization (TESTING=true)")
        return

    try:
        models.Base.metadata.create_all(bind=database.get_main_engine())
        SessionLocal = database.get_session_local()
        db = SessionLocal()
        try:
            user_count = get_user_count(db)
            if user_count == 0:
                seed_users(db)
            sync_db_users(db)
        except DatabaseError as e:
            print(f"Error during startup synchronization: {e.message}")
        finally:
            db.close()
    except Exception as e:
        print(f"Critical error during startup: {e}")


@app.get("/test")
def test_endpoint(db: Session = Depends(database.get_db)):
    """Test endpoint to verify database connectivity."""
    try:
        result = run_test_query(db)
        return {"message": "test successful", "db_result": result}
    except DatabaseError as e:
        return {"message": "test failed", "error": e.message}


@app.post("/login", response_model=schemas.LoginResponse)
async def login(request: schemas.LoginRequest, db: Session = Depends(database.get_db)):
    """Authenticates user via Sybase and returns JWT."""
    try:
        return svc_login_user(db, request.username, request.password)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed: Invalid credentials or database unavailable",
        )


@app.get("/users", response_model=list[schemas.User])
def read_users(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Retrieves all users. Protected by JWT."""
    return svc_get_all_users(db)


@app.get("/db-check")
def db_check(db: Session = Depends(database.get_db)):
    """Checks database connectivity using the main session."""
    try:
        result = run_test_query(db)
        return {"status": "ok", "result": result}
    except DatabaseError as e:
        return {"status": "error", "detail": e.message}


@app.get("/wosmaster", response_model=list[schemas.WOSMaster])
def get_wos_masters(
    customer_code: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    db: Session = Depends(database.get_db),
):
    """Returns WOSMaster records with optional filters."""
    return svc_get_wos_masters(db, customer_code=customer_code, from_date=from_date, to_date=to_date)


@app.get("/wosmaster/{serial_no}", response_model=schemas.WOSMaster)
def get_wos_master(serial_no: int, db: Session = Depends(database.get_db)):
    """Returns a specific WOSMaster record by serial number."""
    return svc_get_wos_master(db, serial_no)


@app.get("/wosline", response_model=list[schemas.WOSLine])
def get_wos_lines(
    wos_serial: Optional[int] = None,
    db: Session = Depends(database.get_db),
):
    """Returns WOSLine records, optionally filtered by WOSSerial."""
    return svc_get_wos_lines(db, wos_serial=wos_serial)


@app.get("/wosline/{wos_serial}/{line_serial}", response_model=schemas.WOSLine)
def get_wos_line(
    wos_serial: int,
    line_serial: int,
    db: Session = Depends(database.get_db),
):
    """Returns a specific WOSLine by WOSSerial and WOSLineSerial."""
    return svc_get_wos_line(db, wos_serial, line_serial)


@app.put("/wosline/{wos_serial}/{line_serial}", response_model=schemas.WOSLine)
def update_wos_line(
    wos_serial: int,
    line_serial: int,
    line_update: schemas.WOSLineUpdate,
    db: Session = Depends(database.get_db),
):
    """Updates VettedQty for a WOSLine. VettedQty cannot exceed AuthorisedQty."""
    return svc_update_wos_line(db, wos_serial, line_serial, line_update.VettedQty)


@app.put("/wosline-bulk", response_model=List[schemas.WOSLine])
def bulk_update_wos_lines(
    bulk_update: schemas.WOSLinesBulkUpdate,
    db: Session = Depends(database.get_db),
):
    """Bulk updates VettedQty for multiple WOSLine records."""
    lines = [
        {"WOSLineSerial": lu.WOSLineSerial, "VettedQty": lu.VettedQty}
        for lu in bulk_update.Lines
    ]
    return svc_bulk_update_wos_lines(db, bulk_update.WOSSerial, lines)


@app.get("/correspondence/{wos_serial}", response_model=list[schemas.Correspondence])
def get_correspondence(wos_serial: int, db: Session = Depends(database.get_db)):
    """Returns correspondence list for a given WOSSerial with descriptions."""
    return svc_get_correspondence(db, wos_serial)


@app.get("/codetable", response_model=list[schemas.CodeTable])
def get_codetable_data(column_name: str, db: Session = Depends(database.get_db)):
    """Returns CodeTable data for a given ColumnName."""
    return svc_get_codetable_data(db, column_name)


@app.post("/forgot-password")
async def forgot_password(
    request: schemas.ForgotPasswordRequest,
    reset_db: Session = Depends(database.get_reset_db),
):
    """Initiates password reset by generating a token. Returns generic message."""
    svc_forgot_password(reset_db, request.email)
    return {"message": "If the email exists, a password reset instruction has been sent."}


@app.post("/reset-password")
async def reset_password(
    request: schemas.ResetPasswordRequest,
    db: Session = Depends(database.get_db),
    reset_db: Session = Depends(database.get_reset_db),
):
    """Resets user password using a valid token."""
    try:
        svc_reset_password(db, reset_db, request.token, request.new_password)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return {"message": "Password reset successful"}

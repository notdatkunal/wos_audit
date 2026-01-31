"""Authentication and password reset business logic."""

import secrets
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import text

import database
import auth as auth_module
from repositories import (
    get_user_by_login_id,
    get_user_email_by_email,
    create_password_reset,
    get_password_reset_by_token,
    delete_password_reset,
    update_sybase_password,
)
from exceptions import DatabaseError, NotFoundError


def login_user(db: Session, username: str, password: str) -> dict:
    """
    Authenticate user via Sybase and return login response with JWT.
    Raises NotFoundError if user not in app DB; other failures raise DatabaseError or return generic auth failure.
    """
    engine = database.get_user_engine(username, password)
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        user = get_user_by_login_id(db, username)
        if not user:
            raise NotFoundError("User authenticated with DB but not found in application database")
        user_roles = [r.RoleName for r in user.roles]
        access_token = auth_module.create_access_token(
            data={"sub": user.LoginId, "roles": user_roles}
        )
        return {
            "message": "Login successful",
            "username": username,
            "name": user.Name,
            "stationCode": user.StationCode,
            "rank": user.Rank,
            "department": user.Department,
            "roles": user_roles,
            "access_token": access_token,
            "token_type": "bearer"
        }
    finally:
        engine.dispose()


def forgot_password(reset_db: Session, email: str) -> None:
    """
    Initiate password reset: find user by email, generate token, store in SQLite.
    Does not reveal whether email exists (generic message).
    """
    mapping = get_user_email_by_email(reset_db, email)
    if mapping:
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=1)
        create_password_reset(reset_db, mapping.username, token, expires_at)


def reset_password(
    db: Session,
    reset_db: Session,
    token: str,
    new_password: str,
) -> None:
    """
    Reset password using token: validate token, update Sybase password, clear token.
    Raises NotFoundError for invalid/expired token.
    """
    reset_info = get_password_reset_by_token(reset_db, token)
    if not reset_info:
        raise NotFoundError("Invalid token")
    if reset_info.expires_at < datetime.now(timezone.utc).replace(tzinfo=None):
        delete_password_reset(reset_db, reset_info)
        raise NotFoundError("Token expired")
    update_sybase_password(db, reset_info.username, new_password)
    delete_password_reset(reset_db, reset_info)

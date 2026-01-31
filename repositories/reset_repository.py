"""Password reset (SQLite) and Sybase password update queries with exception handling."""

from datetime import datetime
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

import reset_models
from exceptions import DatabaseError, NotFoundError


def get_user_email_by_email(db: Session, email: str):
    """Return UserEmail mapping or None. Raises DatabaseError on failure."""
    try:
        return db.query(reset_models.UserEmail).filter(
            reset_models.UserEmail.email == email
        ).first()
    except SQLAlchemyError as e:
        raise DatabaseError("Failed to fetch user email mapping", cause=e)


def create_password_reset(
    db: Session,
    username: str,
    token: str,
    expires_at: datetime,
) -> None:
    """Store password reset token. Raises DatabaseError on failure."""
    try:
        reset_info = reset_models.PasswordReset(
            username=username,
            token=token,
            expires_at=expires_at
        )
        db.add(reset_info)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseError("Failed to create password reset token", cause=e)


def get_password_reset_by_token(db: Session, token: str):
    """Return PasswordReset row or None. Raises DatabaseError on failure."""
    try:
        return db.query(reset_models.PasswordReset).filter(
            reset_models.PasswordReset.token == token
        ).first()
    except SQLAlchemyError as e:
        raise DatabaseError("Failed to fetch password reset by token", cause=e)


def delete_password_reset(db: Session, reset_info) -> None:
    """Delete a PasswordReset record. Raises DatabaseError on failure."""
    try:
        db.delete(reset_info)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseError("Failed to delete password reset", cause=e)


def update_sybase_password(db: Session, username: str, new_password: str) -> None:
    """Execute sp_password to set user password in Sybase. Raises DatabaseError on failure."""
    try:
        db.execute(
            text("EXEC sp_password NULL, :new_password, :username"),
            {"new_password": new_password, "username": username}
        )
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseError("Failed to reset password in database", cause=e)

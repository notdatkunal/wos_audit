"""User-related business logic."""

from sqlalchemy.orm import Session

from repositories import get_all_users as repo_get_all_users


def get_all_users(db: Session) -> list:
    """Return all users."""
    return repo_get_all_users(db)

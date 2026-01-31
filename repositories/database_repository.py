"""Generic database operations (e.g. connectivity check)."""

from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from exceptions import DatabaseError


def run_test_query(db: Session):
    """Execute SELECT 1 and return scalar. Raises DatabaseError on failure."""
    try:
        result = db.execute(text("SELECT 1"))
        return result.scalar()
    except SQLAlchemyError as e:
        raise DatabaseError("Database connectivity check failed", cause=e)

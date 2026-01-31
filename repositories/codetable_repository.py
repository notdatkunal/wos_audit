"""CodeTable database queries with exception handling."""

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

import models
from exceptions import DatabaseError


def get_codetable_by_column_name(db: Session, column_name: str) -> list:
    """Return CodeTable rows for given ColumnName. Raises DatabaseError on failure."""
    try:
        return db.query(models.CodeTable).filter(
            models.CodeTable.ColumnName == column_name
        ).all()
    except SQLAlchemyError as e:
        raise DatabaseError("Failed to fetch code table", cause=e)

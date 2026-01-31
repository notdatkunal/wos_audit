"""CodeTable business logic."""

from sqlalchemy.orm import Session

from repositories import get_codetable_by_column_name


def get_codetable_data(db: Session, column_name: str) -> list:
    """Return CodeTable rows for given ColumnName."""
    return get_codetable_by_column_name(db, column_name)

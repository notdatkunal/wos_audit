"""Correspondence database queries with exception handling."""

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

import models
from exceptions import DatabaseError


def get_correspondence_by_wos_serial(db: Session, wos_serial: int) -> list:
    """Return correspondence list for WOSSerial with CorrespondenceTypeDescription. Raises DatabaseError."""
    try:
        return db.query(
            models.Correspondence,
            models.CodeTable.Description.label("CorrespondenceTypeDescription")
        ).outerjoin(
            models.CodeTable,
            (models.CodeTable.ColumnName == "CorrespondenceType") &
            (models.CodeTable.CodeValue == models.Correspondence.CorrespondenceType)
        ).filter(
            models.Correspondence.TableName == "WOSMaster",
            models.Correspondence.PrimaryKeyValue == str(wos_serial)
        ).all()
    except SQLAlchemyError as e:
        raise DatabaseError("Failed to fetch correspondence", cause=e)

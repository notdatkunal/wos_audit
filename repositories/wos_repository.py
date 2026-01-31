"""WOSMaster and WOSLine database queries with exception handling."""

from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

import models
from exceptions import DatabaseError, NotFoundError
from models import VettedQtyValidationError


def get_wos_masters_with_description(
    db: Session,
    customer_code: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> list:
    """Return WOSMaster rows with WOSTypeDescription. Raises DatabaseError on failure."""
    try:
        query = db.query(
            models.WOSMaster,
            models.CodeTable.Description.label("WOSTypeDescription")
        ).outerjoin(
            models.CodeTable,
            (models.CodeTable.ColumnName == "WOSType") &
            (models.CodeTable.CodeValue == models.WOSMaster.WOSType)
        )
        if customer_code:
            query = query.filter(models.WOSMaster.CustomerCode == customer_code)
        if from_date:
            query = query.filter(models.WOSMaster.DateTimeInitiated >= from_date)
        if to_date:
            query = query.filter(models.WOSMaster.DateTimeInitiated <= to_date)
        return query.all()
    except SQLAlchemyError as e:
        raise DatabaseError("Failed to fetch WOS masters", cause=e)


def get_wos_master_by_serial(db: Session, serial_no: int) -> tuple | None:
    """Return (WOSMaster, WOSTypeDescription) or None. Raises DatabaseError on failure."""
    try:
        return db.query(
            models.WOSMaster,
            models.CodeTable.Description.label("WOSTypeDescription")
        ).outerjoin(
            models.CodeTable,
            (models.CodeTable.ColumnName == "WOSType") &
            (models.CodeTable.CodeValue == models.WOSMaster.WOSType)
        ).filter(models.WOSMaster.WOSSerial == serial_no).first()
    except SQLAlchemyError as e:
        raise DatabaseError("Failed to fetch WOS master by serial", cause=e)


def get_wos_lines(db: Session, wos_serial: Optional[int] = None) -> list:
    """Return WOSLine list, optionally filtered by WOSSerial. Raises DatabaseError on failure."""
    try:
        query = db.query(models.WOSLine)
        if wos_serial is not None:
            query = query.filter(models.WOSLine.WOSSerial == wos_serial)
        return query.all()
    except SQLAlchemyError as e:
        raise DatabaseError("Failed to fetch WOS lines", cause=e)


def get_wos_line(db: Session, wos_serial: int, line_serial: int):
    """Return WOSLine or None. Raises DatabaseError on failure."""
    try:
        return db.query(models.WOSLine).filter(
            models.WOSLine.WOSSerial == wos_serial,
            models.WOSLine.WOSLineSerial == line_serial
        ).first()
    except SQLAlchemyError as e:
        raise DatabaseError("Failed to fetch WOS line", cause=e)


def update_wos_line_vetted_qty(
    db: Session,
    wos_serial: int,
    line_serial: int,
    vetted_qty: float,
):
    """
    Update VettedQty for a WOSLine. Returns refreshed WOSLine.
    Raises NotFoundError, DatabaseError, or VettedQtyValidationError.
    """
    try:
        line = db.query(models.WOSLine).filter(
            models.WOSLine.WOSSerial == wos_serial,
            models.WOSLine.WOSLineSerial == line_serial
        ).first()
        if not line:
            raise NotFoundError("WOSLine not found")
        line.VettedQty = vetted_qty
        db.commit()
        db.refresh(line)
        return line
    except NotFoundError:
        raise
    except VettedQtyValidationError:
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseError("Failed to update WOS line", cause=e)


def bulk_update_wos_lines_vetted_qty(
    db: Session,
    wos_serial: int,
    line_updates: list[tuple[int, float]],
) -> list:
    """
    Bulk update VettedQty for WOSLines. line_updates: [(WOSLineSerial, VettedQty), ...].
    Returns list of refreshed WOSLine. Raises NotFoundError, DatabaseError, or VettedQtyValidationError.
    """
    try:
        updated = []
        for line_serial, vetted_qty in line_updates:
            line = db.query(models.WOSLine).filter(
                models.WOSLine.WOSSerial == wos_serial,
                models.WOSLine.WOSLineSerial == line_serial
            ).first()
            if not line:
                raise NotFoundError(
                    f"WOSLine with LineSerial {line_serial} not found for WosSerial {wos_serial}"
                )
            line.VettedQty = vetted_qty
            updated.append(line)
        db.commit()
        for line in updated:
            db.refresh(line)
        return updated
    except NotFoundError:
        db.rollback()
        raise
    except VettedQtyValidationError:
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseError("Failed to bulk update WOS lines", cause=e)

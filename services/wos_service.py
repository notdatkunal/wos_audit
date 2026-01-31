"""WOSMaster and WOSLine business logic."""

from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from models import VettedQtyValidationError
from repositories import (
    get_wos_masters_with_description,
    get_wos_master_by_serial as repo_get_wos_master,
    get_wos_lines as repo_get_wos_lines,
    get_wos_line as repo_get_wos_line,
    update_wos_line_vetted_qty,
    bulk_update_wos_lines_vetted_qty,
)
from exceptions import NotFoundError


def _master_to_dict(master, description):
    """Build WOSMaster response dict with WOSTypeDescription."""
    m_dict = {c.name: getattr(master, c.name) for c in master.__table__.columns}
    m_dict["WOSTypeDescription"] = description
    return m_dict


def get_wos_masters(
    db: Session,
    customer_code: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> list:
    """Return WOSMaster list with WOSTypeDescription."""
    results = get_wos_masters_with_description(
        db, customer_code=customer_code, from_date=from_date, to_date=to_date
    )
    return [_master_to_dict(master, desc) for master, desc in results]


def get_wos_master_by_serial(db: Session, serial_no: int) -> dict:
    """Return single WOSMaster by serial or raise NotFoundError."""
    result = repo_get_wos_master(db, serial_no)
    if not result:
        raise NotFoundError("WOSMaster not found")
    master, description = result
    return _master_to_dict(master, description)


def get_wos_lines(db: Session, wos_serial: Optional[int] = None) -> list:
    """Return WOSLine list, optionally filtered by WOSSerial."""
    return repo_get_wos_lines(db, wos_serial=wos_serial)


def get_wos_line(db: Session, wos_serial: int, line_serial: int):
    """Return single WOSLine or raise NotFoundError."""
    line = repo_get_wos_line(db, wos_serial, line_serial)
    if not line:
        raise NotFoundError("WOSLine not found")
    return line


def update_wos_line(
    db: Session,
    wos_serial: int,
    line_serial: int,
    vetted_qty: float,
):
    """
    Update VettedQty for a WOSLine. Validates VettedQty <= AuthorisedQty.
    Returns updated WOSLine. Raises NotFoundError or VettedQtyValidationError.
    """
    line = repo_get_wos_line(db, wos_serial, line_serial)
    if not line:
        raise NotFoundError("WOSLine not found")
    if vetted_qty > line.AuthorisedQty:
        raise VettedQtyValidationError(
            f"VettedQty ({vetted_qty}) cannot be greater than AuthorisedQty ({line.AuthorisedQty})"
        )
    return update_wos_line_vetted_qty(db, wos_serial, line_serial, vetted_qty)


def bulk_update_wos_lines(
    db: Session,
    wos_serial: int,
    lines: List[dict],
):
    """
    Bulk update VettedQty. lines: [{"WOSLineSerial": int, "VettedQty": float}, ...].
    Validates each VettedQty <= AuthorisedQty. Returns list of updated WOSLine.
    """
    for item in lines:
        line = repo_get_wos_line(db, wos_serial, item["WOSLineSerial"])
        if not line:
            raise NotFoundError(
                f"WOSLine with LineSerial {item['WOSLineSerial']} not found for WosSerial {wos_serial}"
            )
        if item.get("VettedQty") is not None and item["VettedQty"] > line.AuthorisedQty:
            raise VettedQtyValidationError(
                f"VettedQty ({item['VettedQty']}) cannot be greater than AuthorisedQty ({line.AuthorisedQty}) for LineSerial {item['WOSLineSerial']}"
            )
    line_updates = [(item["WOSLineSerial"], item["VettedQty"]) for item in lines]
    return bulk_update_wos_lines_vetted_qty(db, wos_serial, line_updates)

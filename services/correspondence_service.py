"""Correspondence business logic."""

from sqlalchemy.orm import Session

from repositories import get_correspondence_by_wos_serial


def get_correspondence(db: Session, wos_serial: int) -> list:
    """Return correspondence list for WOSSerial with CorrespondenceTypeDescription."""
    results = get_correspondence_by_wos_serial(db, wos_serial)
    output = []
    for correspondence, description in results:
        c_dict = {
            c.name: getattr(correspondence, c.name)
            for c in correspondence.__table__.columns
        }
        c_dict["CorrespondenceTypeDescription"] = description
        output.append(c_dict)
    return output

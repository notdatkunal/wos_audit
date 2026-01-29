from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Numeric, Text, CheckConstraint
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    """
    SQLAlchemy model for the 'user' table.
    """
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(100))

    # Relationship with UserRole
    roles = relationship("UserRole", back_populates="user")

class UserRole(Base):
    """
    SQLAlchemy model for the 'userrole' table.
    """
    __tablename__ = "userrole"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    role_name = Column(String(50), nullable=False)

    # Relationship with User
    user = relationship("User", back_populates="roles")

class WOSMaster(Base):
    """
    SQLAlchemy model for the 'WOSMaster' table.
    """
    __tablename__ = "WOSMaster"

    WOSSerial = Column(Integer, primary_key=True, nullable=False)
    CustomerCode = Column(String(4), nullable=False)
    WOSType = Column(String(3), nullable=False)
    InitiatedBy = Column(String(8), nullable=False)
    DateTimeInitiated = Column(DateTime, nullable=False)
    ConcurredBy = Column(String(8))
    DateTimeConcurred = Column(DateTime)
    WONumber = Column(String(50))
    WOIDate = Column(DateTime)
    ApprovedBy = Column(String(8))
    DateTimeApproved = Column(DateTime)
    SanctionNo = Column(String(50))
    SanctionDate = Column(DateTime)
    ClosedBy = Column(String(8))
    DateTimeClosed = Column(DateTime)
    Remarks = Column(String(255))

    # Relationship with WOSLine
    lines = relationship("WOSLine", back_populates="master")

class WOSLine(Base):
    """
    SQLAlchemy model for the 'WOSLine' table.
    """
    __tablename__ = "WOSLine"

    WOSSerial = Column(Integer, ForeignKey("WOSMaster.WOSSerial"), primary_key=True, nullable=False)
    WOSLineSerial = Column(Integer, primary_key=True, nullable=False)
    ItemCode = Column(String(32), nullable=False)
    ItemDesc = Column(String(60), nullable=False)
    ItemDeno = Column(String(3), nullable=False)
    SOS = Column(String(3), nullable=False)
    AuthorisedQty = Column(Float, nullable=False)
    ReceivedQty = Column(Float)
    BalanceQty = Column(Float)
    ReviewedQty = Column(Float)
    VettedQty = Column(Float)
    RecommendedQty = Column(Float)
    DateFromWhichHeld = Column(DateTime)
    AuthorityRef = Column(String(255), nullable=False)
    AuthorityDate = Column(DateTime, nullable=False)
    Justification = Column(String(255), nullable=False)
    Price = Column(Numeric(19, 4), CheckConstraint('Price >= 0'))
    TotalCost = Column(Numeric(19, 4), CheckConstraint('TotalCost >= 0'))
    Remarks = Column(Text)
    ClosedBy = Column(String(8))
    DateTimeClosed = Column(DateTime)

    # Relationship with WOSMaster
    master = relationship("WOSMaster", back_populates="lines")

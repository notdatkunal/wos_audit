from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Numeric, Text, CheckConstraint, LargeBinary
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    """
    SQLAlchemy model for the 'Users' table.
    """
    __tablename__ = "Users"

    LoginId = Column(String(8), primary_key=True, nullable=False)
    Id = Column(String(8), nullable=False)
    Name = Column(String(30), nullable=False)
    Rank = Column(String(10), nullable=False)
    Department = Column(String(8), nullable=False)
    DateTimeJoined = Column(DateTime, nullable=False)
    DateTimeLeft = Column(DateTime)
    StationCode = Column(String(1), nullable=False)

    __table_args__ = (
        CheckConstraint("StationCode IN ('K','U','B','V','D','P','A','G')", name="chk_Users_Stn_cd"),
        CheckConstraint("LoginId LIKE '[a-zA-Z]%'", name="Users_LoginId"),
    )

    # Relationship with UserRole
    roles = relationship("UserRole", back_populates="user")

class UserRole(Base):
    """
    SQLAlchemy model for the 'UserRole' table.
    """
    __tablename__ = "UserRole"

    LoginId = Column(String(8), ForeignKey("Users.LoginId"), primary_key=True, nullable=False)
    RoleName = Column(String(15), primary_key=True, nullable=False)
    DateTimeActivated = Column(DateTime, nullable=False)
    DateTimeClosed = Column(DateTime)
    StationCode = Column(String(1), primary_key=True, nullable=False)

    __table_args__ = (
        CheckConstraint("StationCode IN ('K','U','B','V','D','P','A','G')", name="chk_UserRol_Stn_cd"),
    )

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
    Price = Column(Numeric(19, 4))
    TotalCost = Column(Numeric(19, 4))
    Remarks = Column(Text)
    ClosedBy = Column(String(8))
    DateTimeClosed = Column(DateTime)

    __table_args__ = (
        CheckConstraint('Price >= 0', name='Chk_Price'),
        CheckConstraint('TotalCost >= 0', name='Chk_TotalCost'),
    )

    # Relationship with WOSMaster
    master = relationship("WOSMaster", back_populates="lines")

class CodeTable(Base):
    """
    SQLAlchemy model for the 'CodeTable' table.
    """
    __tablename__ = "CodeTable"

    ColumnName = Column(String(30), primary_key=True, nullable=False)
    CodeValue = Column(String(10), primary_key=True, nullable=False)
    Description = Column(String(30))

class Correspondence(Base):
    """
    SQLAlchemy model for the 'Correspondence' table.
    """
    __tablename__ = "Correspondence"

    LineNo = Column(Integer, primary_key=True, nullable=False)
    TableName = Column(String(30), primary_key=True, nullable=False)
    PrimaryKeyValue = Column(String(120), primary_key=True, nullable=False)
    RoleName = Column(String(15), nullable=False)
    CorrespondenceBy = Column(String(8), nullable=False)
    CorrespondenceToRole = Column(String(15), nullable=False)
    DateTimeCorrespondence = Column(DateTime, nullable=False)
    CorrespondenceType = Column(String(5), nullable=False)
    StationCode = Column(String(1), nullable=False)
    Remarks = Column(String(255))
    DocumentType = Column(String(30))
    Document = Column(LargeBinary)
    CorrespondenceChoice = Column(String(1))

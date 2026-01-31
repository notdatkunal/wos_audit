from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class LoginRequest(BaseModel):
    """
    Schema for login request.
    """
    username: str
    password: str

class LoginResponse(BaseModel):
    """
    Schema for login response.
    """
    message: str
    username: str
    name: str
    stationCode: str
    rank: str
    department: str
    roles: List[str]
    access_token: str
    token_type: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserRoleBase(BaseModel):
    RoleName: str
    DateTimeActivated: datetime
    DateTimeClosed: Optional[datetime] = None
    StationCode: str

class UserRole(UserRoleBase):
    LoginId: str

    model_config = ConfigDict(from_attributes=True)

class UserBase(BaseModel):
    LoginId: str
    Id: str
    Name: str
    Rank: str
    Department: str
    DateTimeJoined: datetime
    DateTimeLeft: Optional[datetime] = None
    StationCode: str

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class User(UserBase):
    roles: List[UserRole] = []

    model_config = ConfigDict(from_attributes=True)

class WOSLineBase(BaseModel):
    WOSSerial: int
    WOSLineSerial: int
    ItemCode: str
    ItemDesc: str
    ItemDeno: str
    SOS: str
    AuthorisedQty: float
    ReceivedQty: Optional[float] = None
    BalanceQty: Optional[float] = None
    ReviewedQty: Optional[float] = None
    VettedQty: Optional[float] = None
    RecommendedQty: Optional[float] = None
    DateFromWhichHeld: Optional[datetime] = None
    AuthorityRef: str
    AuthorityDate: datetime
    Justification: str
    Price: Optional[float] = None
    TotalCost: Optional[float] = None
    Remarks: Optional[str] = None
    ClosedBy: Optional[str] = None
    DateTimeClosed: Optional[datetime] = None

class WOSLine(WOSLineBase):
    model_config = ConfigDict(from_attributes=True)

class WOSLineUpdate(BaseModel):
    VettedQty: float

class WOSMasterBase(BaseModel):
    WOSSerial: int
    CustomerCode: str
    WOSType: str
    InitiatedBy: str
    DateTimeInitiated: datetime
    ConcurredBy: Optional[str] = None
    DateTimeConcurred: Optional[datetime] = None
    WONumber: Optional[str] = None
    WOIDate: Optional[datetime] = None
    ApprovedBy: Optional[str] = None
    DateTimeApproved: Optional[datetime] = None
    SanctionNo: Optional[str] = None
    SanctionDate: Optional[datetime] = None
    ClosedBy: Optional[str] = None
    DateTimeClosed: Optional[datetime] = None
    Remarks: Optional[str] = None

class WOSMaster(WOSMasterBase):
    model_config = ConfigDict(from_attributes=True)

class WOSMasterWithLines(WOSMasterBase):
    lines: List[WOSLine] = []
    model_config = ConfigDict(from_attributes=True)

class CodeTableBase(BaseModel):
    ColumnName: str
    CodeValue: str
    Description: Optional[str] = None

class CodeTable(CodeTableBase):
    model_config = ConfigDict(from_attributes=True)

class CorrespondenceBase(BaseModel):
    LineNo: int
    TableName: str
    PrimaryKeyValue: str
    RoleName: str
    CorrespondenceBy: str
    CorrespondenceToRole: str
    DateTimeCorrespondence: datetime
    CorrespondenceType: str
    StationCode: str
    Remarks: Optional[str] = None
    DocumentType: Optional[str] = None
    CorrespondenceChoice: Optional[str] = None
    CorrespondenceTypeDescription: Optional[str] = None


class Correspondence(CorrespondenceBase):
    model_config = ConfigDict(from_attributes=True)

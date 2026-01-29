from pydantic import BaseModel, ConfigDict
from typing import List, Optional

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
    access_token: str
    token_type: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserRoleBase(BaseModel):
    role_name: str

class UserRole(UserRoleBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)

class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = None

class User(UserBase):
    id: int
    roles: List[UserRole] = []

    model_config = ConfigDict(from_attributes=True)

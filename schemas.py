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

class UserRoleBase(BaseModel):
    role_name: str

class UserRole(UserRoleBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)

class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class User(UserBase):
    id: int
    roles: List[UserRole] = []

    model_config = ConfigDict(from_attributes=True)

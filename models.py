from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
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
    email = Column(String(100), unique=True, index=True)
    reset_token = Column(String(100), index=True, nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)

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

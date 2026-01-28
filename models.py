from sqlalchemy import Column, Integer, String, ForeignKey
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

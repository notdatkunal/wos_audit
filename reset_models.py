from sqlalchemy import Column, Integer, String, DateTime
from database import ResetBase, get_reset_engine

class UserEmail(ResetBase):
    """
    SQLAlchemy model for mapping usernames to emails in SQLite.
    Since we cannot change the Sybase schema, we store this mapping here.
    """
    __tablename__ = "user_email"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)

class PasswordReset(ResetBase):
    """
    SQLAlchemy model for storing password reset tokens in SQLite.
    """
    __tablename__ = "password_reset"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), index=True, nullable=False)
    token = Column(String(100), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)

# Create the tables in SQLite
ResetBase.metadata.create_all(bind=get_reset_engine())

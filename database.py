import os
import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

SYBASE_SERVER = os.getenv("SYBASE_SERVER")
SYBASE_PORT = os.getenv("SYBASE_PORT")
SYBASE_DB = os.getenv("SYBASE_DB")
MAIN_DB_USER = os.getenv("MAIN_DB_USER")
MAIN_DB_PASS = os.getenv("MAIN_DB_PASS")

def get_connection_url(username, password):
    """
    Constructs the connection URL for Sybase ASE using pyodbc.
    Safely handles credentials to prevent connection string injection and
    uses URL encoding for the connection parameters.
    """
    def escape_odbc_value(val):
        """
        Escapes values for ODBC connection strings by wrapping them in braces.
        """
        if val is None:
            return ""
        return "{" + str(val).replace("}", "}}") + "}"

    driver = os.getenv("DB_DRIVER", "{Adaptive Server Enterprise}")

    odbc_connect = (
        f"DRIVER={driver};"
        f"Server={SYBASE_SERVER};"
        f"Port={SYBASE_PORT};"
        f"Database={SYBASE_DB};"
        f"Uid={escape_odbc_value(username)};"
        f"Pwd={escape_odbc_value(password)};"
    )

    # Add optional TDS_Version if provided (useful for FreeTDS)
    tds_version = os.getenv("TDS_VERSION")
    if tds_version:
        odbc_connect += f"TDS_Version={tds_version};"

    # URL encode the entire odbc_connect string for the SQLAlchemy URL
    encoded_params = urllib.parse.quote_plus(odbc_connect)
    return f"sybase+pyodbc:///?odbc_connect={encoded_params}"

# Use a lazy initialization for the main engine and session factory
_main_engine = None
_SessionLocal = None

_reset_engine = None
_ResetSessionLocal = None

SQLITE_URL = "sqlite:///./password_reset.db"

def get_main_engine():
    global _main_engine
    if _main_engine is None:
        _main_engine = create_engine(get_connection_url(MAIN_DB_USER, MAIN_DB_PASS))
    return _main_engine

def get_session_local():
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_main_engine()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _SessionLocal

def get_reset_engine():
    global _reset_engine
    if _reset_engine is None:
        _reset_engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
    return _reset_engine

def get_reset_session_local():
    global _ResetSessionLocal
    if _ResetSessionLocal is None:
        engine = get_reset_engine()
        _ResetSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _ResetSessionLocal

Base = declarative_base()
ResetBase = declarative_base()

def get_user_engine(username, password):
    """
    Creates a temporary engine to verify user credentials.
    """
    url = get_connection_url(username, password)
    return create_engine(url)

def get_db():
    """
    Dependency to get the global DB session (Sybase).
    """
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_reset_db():
    """
    Dependency to get the password reset DB session (SQLite).
    """
    ResetSessionLocal = get_reset_session_local()
    db = ResetSessionLocal()
    try:
        yield db
    finally:
        db.close()

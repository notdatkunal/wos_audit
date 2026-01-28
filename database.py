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

    odbc_connect = (
        f"DRIVER={{Adaptive Server Enterprise}};"
        f"Server={SYBASE_SERVER};"
        f"Port={SYBASE_PORT};"
        f"Database={SYBASE_DB};"
        f"Uid={escape_odbc_value(username)};"
        f"Pwd={escape_odbc_value(password)};"
    )
    # URL encode the entire odbc_connect string for the SQLAlchemy URL
    encoded_params = urllib.parse.quote_plus(odbc_connect)
    return f"sybase+pyodbc:///?odbc_connect={encoded_params}"

# Use a lazy initialization for the main engine and session factory
_main_engine = None
_SessionLocal = None

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

Base = declarative_base()

def get_user_engine(username, password):
    """
    Creates a temporary engine to verify user credentials.
    """
    url = get_connection_url(username, password)
    return create_engine(url)

def get_db():
    """
    Dependency to get the global DB session.
    """
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

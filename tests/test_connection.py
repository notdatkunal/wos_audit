import os
import pyodbc
from dotenv import load_dotenv

load_dotenv()

SYBASE_SERVER = os.getenv("SYBASE_SERVER")
SYBASE_PORT = os.getenv("SYBASE_PORT")
SYBASE_DB = os.getenv("SYBASE_DB")
MAIN_DB_USER = os.getenv("MAIN_DB_USER")
MAIN_DB_PASS = os.getenv("MAIN_DB_PASS")
DB_DRIVER = os.getenv("DB_DRIVER", "{Adaptive Server Enterprise}")

def test_conn():
    print("--- ODBC Drivers ---")
    drivers = pyodbc.drivers()
    for d in drivers:
        print(f"Driver: {d}")
    
    print("\n--- Connection Details ---")
    print(f"Server: {SYBASE_SERVER}")
    print(f"Port: {SYBASE_PORT}")
    print(f"DB: {SYBASE_DB}")
    print(f"User: {MAIN_DB_USER}")
    
    # Try different driver names if the default fails
    driver_names = [DB_DRIVER, "{SAP ASE ODBC Driver}", "{Adaptive Server Enterprise}"]
    
    for driver_name in driver_names:
        print(f"\nTrying driver: {driver_name}")
        conn_str = (
            f"DRIVER={driver_name};"
            f"Server={SYBASE_SERVER};"
            f"Port={SYBASE_PORT};"
            f"Database={SYBASE_DB};"
            f"Uid={MAIN_DB_USER};"
            f"Pwd={MAIN_DB_PASS};"
        )
        try:
            conn = pyodbc.connect(conn_str, timeout=5)
            print(f"SUCCESS with {driver_name}!")
            conn.close()
            return
        except Exception as e:
            print(f"Failed with {driver_name}: {e}")

if __name__ == "__main__":
    test_conn()

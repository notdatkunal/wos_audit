print("Starting import check...")
try:
    print("Importing database...")
    import database
    print("Importing models...")
    import models
    print("Importing reset_models...")
    import reset_models
    print("Importing schemas...")
    import schemas
    print("Importing auth...")
    import auth
    print("Importing main...")
    import main
    print("All imports successful!")
except Exception as e:
    print(f"Import failed: {e}")

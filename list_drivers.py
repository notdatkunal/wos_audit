import pyodbc
drivers = [x for x in pyodbc.drivers()]
print("Available ODBC Drivers:")
for driver in drivers:
    print(f"- {driver}")

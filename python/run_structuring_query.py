"""
Run the structuring detection query against synthetic data using DuckDB.
"""

import duckdb
import os
from pathlib import Path

# Adjust this path if your script lives elsewhere
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SQL_DIR = BASE_DIR / "sql"

# Connect to an in-memory DuckDB database
con = duckdb.connect(":memory:")

# Create tables from CSVs
con.execute("""
CREATE TABLE customers AS SELECT * FROM read_csv_auto('{}')
""".format(DATA_DIR / "customers.csv"))

con.execute("""
CREATE TABLE accounts AS SELECT * FROM read_csv_auto('{}')
""".format(DATA_DIR / "accounts.csv"))

con.execute("""
CREATE TABLE merchants AS SELECT * FROM read_csv_auto('{}')
""".format(DATA_DIR / "merchants.csv"))

con.execute("""
CREATE TABLE locations AS SELECT * FROM read_csv_auto('{}')
""".format(DATA_DIR / "locations.csv"))

con.execute("""
CREATE TABLE transactions AS SELECT * FROM read_csv_auto('{}')
""".format(DATA_DIR / "transactions_raw.csv"))

# Load and run the structuring query
query_path = SQL_DIR / "01_structuring_detection.sql"
with open(query_path, "r", encoding="utf-8") as f:
    query_sql = f.read()

result = con.execute(query_sql).fetchdf()

print("Structuring detection results:")
print(result)

# Optional: save results to CSV
output_path = DATA_DIR / "structuring_flags.csv"
result.to_csv(output_path, index=False)
print(f"\nResults saved to {output_path}")

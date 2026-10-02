"""
Run AML/fraud detection queries against synthetic data using DuckDB.
Executes:
- 01_structuring_detection.sql
- 02_velocity_anomalies.sql
"""

import duckdb
import os
from pathlib import Path

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

# Helper to run a query file and save results
def run_query_file(query_filename, output_filename):
    query_path = SQL_DIR / query_filename
    with open(query_path, "r", encoding="utf-8") as f:
        query_sql = f.read()

    result = con.execute(query_sql).fetchdf()
    print(f"\n=== {query_filename} ===")
    print(result)

    output_path = DATA_DIR / output_filename
    result.to_csv(output_path, index=False)
    print(f"Results saved to {output_path}")
    return result

# 1) Structuring detection
structuring_result = run_query_file(
    "01_structuring_detection.sql",
    "structuring_flags.csv"
)

# 2) Velocity anomalies
velocity_result = run_query_file(
    "02_velocity_anomalies.sql",
    "velocity_flags.csv"
)

print("\nAll queries executed successfully.")

import duckdb
import os
import pandas as pd

# Connect to the DuckDB database (relative to nppes_dbt)
conn = duckdb.connect("nppes.duckdb")

# Base path for sample data
base_path = "../sample_data"

# Define tables and corresponding CSVs
tables = {
    "api_data": "api_data.csv",
    "npi_data": "npi_data.csv",
    "nppes_sample": "nppes_sample.csv",
    "nucc_taxonomy": "nucc_taxonomy.csv",
    "ssa_fips_state_county": "ssa_fips_state_county.csv",
    "zip_data": "zip_data.csv",
}

# Ensure the schema exists
conn.execute("CREATE SCHEMA IF NOT EXISTS main;")

for table, filename in tables.items():
    file_path = os.path.join(base_path, filename)
    print(f"Loading {table} from {file_path}")
    
    # Read CSV into pandas
    df = pd.read_csv(file_path, dtype=str)
    
    # Only remove quotes from headers for npi_data and nppes_sample
    if table in ["npi_data", "nppes_sample"]:
        df.columns = [c.replace('"', '') for c in df.columns]

    # Create or replace table in DuckDB
    conn.execute(f"CREATE OR REPLACE TABLE main.{table} AS SELECT * FROM df")

conn.close()
print("Sample data loaded successfully!")

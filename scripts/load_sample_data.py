import duckdb
import os

conn = duckdb.connect("nppes.duckdb")

tables = {
    "api_data": "sample_data/api_data.csv",
    "npi_data": "sample_data/npi_data.csv",
    "nppes_sample": "sample_data/nppes_sample.csv",
    "nucc_taxonomy": "sample_data/nucc_taxonomy.csv",
    "ssa_fips_state_county": "sample_data/ssa_fips_state_county.csv",
    "zip_data": "sample_data/zip_data.csv",
}

for table, path in tables.items():
    conn.execute(f"""
        CREATE OR REPLACE TABLE main.{table} AS
        SELECT * FROM read_csv_auto('{path}')
    """)

conn.close()

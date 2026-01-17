import duckdb
import os
conn = duckdb.connect("../nppes.duckdb")
base_path = "../sample_data"
tables = {
    "api_data": "api_data.csv",
    "npi_data": "npi_data.csv",
    "nppes_sample": "nppes_sample.csv",
    "nucc_taxonomy": "nucc_taxonomy.csv",
    "ssa_fips_state_county": "ssa_fips_state_county.csv",
    "zip_data": "zip_data.csv",
}

for table, filename in tables.items():
    file_path = os.path.join(base_path, filename)
    print(f"Loading {table} from {file_path}")
    conn.execute(f"""
        CREATE OR REPLACE TABLE main.{table} AS
        SELECT * FROM read_csv_auto('{file_path}', header=true,ALL_VARCHAR=TRUE,normalize_names = false ,quote='\"')
    """)

conn.close()

import duckdb
import os


DB_PATH = "../nppes.duckdb"
BASE_PATH = "../sample_data"

# Files that require explicit CSV parsing
STRICT_TABLES = {
    "npi_data": "npi_data.csv",
    "nppes_sample": "nppes_sample.csv",
}

# Files that can be safely auto-detected
AUTO_TABLES = {
    "api_data": "api_data.csv",
    "nucc_taxonomy": "nucc_taxonomy.csv",
    "ssa_fips_state_county": "ssa_fips_state_county.csv",
    "zip_data": "zip_data.csv",
}


# Load data

conn = duckdb.connect(DB_PATH)

# 1️ Load tables with complex headers (FIX)
for table, filename in STRICT_TABLES.items():
    file_path = os.path.join(BASE_PATH, filename)
    print(f"Loading {table} (robust CSV mode)")
    conn.execute(f"""
        CREATE OR REPLACE TABLE main.{table} AS
        SELECT *
        FROM read_csv(
            '{file_path}',
            header=true,
            delim=',',
            quote='"',
            escape='"',
            normalize_names=true,
            all_varchar=true,
            strict_mode=false,
            ignore_errors=true,
            null_padding=true,
            max_line_size=10000000
        )
    """)

# 2️ Load remaining tables (unchanged)
for table, filename in AUTO_TABLES.items():
    file_path = os.path.join(BASE_PATH, filename)
    print(f"Loading {table} (auto CSV parsing)")
    conn.execute(f"""
        CREATE OR REPLACE TABLE main.{table} AS
        SELECT *
        FROM read_csv_auto(
            '{file_path}',
            header=true,
            normalize_names=true,
            all_varchar=true
        )
    """)


# Validation 
print("\nColumn counts:")
for table in list(STRICT_TABLES.keys()) + list(AUTO_TABLES.keys()):
    cols = conn.execute(f"PRAGMA table_info('{table}')").fetchall()
    print(f"{table}: {len(cols)} columns")

conn.close()

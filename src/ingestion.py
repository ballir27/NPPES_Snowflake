from io import BytesIO
import os
import csv
from dotenv import load_dotenv
import polars as pl
import duckdb
import boto3
import time
from local_logging import get_logger

logger = get_logger("extract")
load_dotenv()

# AWS Configuration
aws_region_name = os.getenv("AWS_REGION_NAME")
aws_bucket = os.getenv("aws_bucket_name")
aws_team_folder = os.getenv("team_folder")
aws_session = boto3.Session(profile_name=os.getenv("sso_profile_name"))
aws_s3_client = aws_session.client('s3')

# File Names
npi_csv_file = os.getenv("npi_csv_data")
nucc_taxonomy_file = os.getenv("nucc_taxonomy")
nppes_sample_file = os.getenv("nppes_sample")
ssa_fips_state_county_file = os.getenv("ssa_fips_state_county")
zip_csv_file = os.getenv("zip_csv")
api_csv_file = os.getenv("api_csv")

LARGE_FILE_THRESHOLD_GB = 2

def is_large_file(aws_session, aws_bucket, s3_key, threshold_gb=LARGE_FILE_THRESHOLD_GB):
    s3 = aws_session.client('s3')
    size = s3.head_object(Bucket=aws_bucket, Key=s3_key)['ContentLength']
    size_gb = size / (1024 ** 3)
    return size_gb > threshold_gb

def ingestion_data_into_duckdb(aws_session):
    try:
        aws_credentials = aws_session.get_credentials().get_frozen_credentials()
        
        with duckdb.connect("NPPES.duckdb") as duck_conn:  
            # 1. Setup Extensions and S3 Auth
            duck_conn.execute("INSTALL aws; LOAD aws;")
            duck_conn.execute(f""" 
                CREATE OR REPLACE SECRET s3_auth (
                    TYPE S3,
                    KEY_ID '{aws_credentials.access_key}', 
                    SECRET '{aws_credentials.secret_key}', 
                    SESSION_TOKEN '{aws_credentials.token}', 
                    REGION '{aws_region_name}'
                );
            """)                                            
            
            # 2. Performance Tuning
            duck_conn.execute("PRAGMA threads=8;")
            duck_conn.execute("SET preserve_insertion_order=false;")
            duck_conn.execute("SET max_memory='6GB';") 
            duck_conn.execute("SET temp_directory='duckdb_temp';")

            # 3. Connection Test
            logger.info("Verifying S3 connection...")
            test_path = f"s3://{aws_bucket}/{aws_team_folder}/{npi_csv_file}"
            duck_conn.execute(f"SELECT 1 FROM read_csv_auto('{test_path}', ALL_VARCHAR=TRUE) LIMIT 1").fetchall()
            logger.info("S3 Connection Verified.")

            # 4. Define File Map
            files = {
                "npi_data": {"path": npi_csv_file, "type": "csv"},
                "nucc_taxonomy": {"path": nucc_taxonomy_file, "type": "csv"},
                "nppes_sample": {"path": nppes_sample_file, "type": "csv"},
                "ssa_fips_state_county": {"path": ssa_fips_state_county_file, "type": "csv"},
                "zip_data": {"path": zip_csv_file, "type": "excel"},
                "api_data": {"path": api_csv_file, "type": "csv"}
            }

            # 5. Main Ingestion Loop
            for table_name, file_info in files.items():
                start_time = time.time()
                s3_path = f"s3://{aws_bucket}/{aws_team_folder}/{file_info['path']}"
                s3_key = f"{aws_team_folder}/{file_info['path']}"
                
                # Check if table already exists to skip re-downloading
                table_exists = duck_conn.execute(f"SELECT count(*) FROM information_schema.tables WHERE table_name = '{table_name}'").fetchone()[0]
                if table_exists > 0:
                    logger.info(f"Table {table_name} already exists. Skipping...")
                    continue
                
                try:
                    large_file = is_large_file(aws_session, aws_bucket, s3_key)
                    
                    if file_info["type"] == "csv" and large_file:
                        logger.info(f"Starting Large Ingestion: {table_name}...")
                        duck_conn.execute(f"""
                            CREATE OR REPLACE TABLE {table_name} AS
                            SELECT * FROM read_csv_auto('{s3_path}', header=TRUE, parallel=TRUE, ALL_VARCHAR=TRUE, QUOTE='\"', IGNORE_ERRORS=TRUE)
                        """)
                    elif file_info["type"] == "excel":
                        logger.info(f"Reading Excel: {table_name}...")
                        response = aws_s3_client.get_object(Bucket=aws_bucket, Key=s3_key)
                        excel_data = response['Body'].read()
                        raw_data = pl.read_excel(BytesIO(excel_data))
                        duck_conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM raw_data")
                    elif file_info["type"] == "csv":
                        logger.info(f"Reading small CSV: {table_name}...")
                        duck_conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM read_csv_auto('{s3_path}')")

                    duration = round((time.time() - start_time) / 60, 2)
                    logger.info(f" {table_name} completed in {duration} minutes.")

                except Exception as path_err:
                    logger.error(f"Error processing {table_name}: {path_err}")
                    continue

            # 6. Final Export to Parquet (Outside the loop, inside the connection block)
            if not os.path.exists("npi_data_optimized.parquet"):
                logger.info(" Creating optimized Parquet backup for NPI data...")
                duck_conn.execute("COPY npi_data TO 'npi_data_optimized.parquet' (FORMAT PARQUET, CODEC 'ZSTD');")
                logger.info(" Parquet backup created: npi_data_optimized.parquet")
            else:
                logger.info(" Parquet backup already exists. Skipping export.")

        logger.info(" All data loaded successfully.")

    except Exception as e:  
        logger.error(f"Critical Error: {e}", exc_info=True)
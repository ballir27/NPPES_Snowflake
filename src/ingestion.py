from io import BytesIO
import os
import csv
from dotenv import load_dotenv
from importlib_metadata import files
import polars as pl
# import duckdb
import snowflake.connector
from adbc_driver_snowflake import dbapi
import boto3
import time
from local_logging import get_logger

logger = get_logger("ingestion")
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

def ingest_into_snowflake(aws_session, snowflake_config):
    try:
        # 1. Get AWS Credentials
        aws_credentials = aws_session.get_credentials().get_frozen_credentials()                          
            
        # 2. Establish Snowflake Connection
        conn= snowflake.connector.connect(**snowflake_config)
        curr = conn.cursor()

        # 3. Setup Environment
        curr.execute(f"CREATE DATABASE IF NOT EXISTS {snowflake_config['database']};")
        curr.execute(f"USE DATABASE {snowflake_config['database']};")
        
        curr.execute(f"CREATE SCHEMA IF NOT EXISTS {snowflake_config['schema']};")
        curr.execute(f"USE SCHEMA {snowflake_config['schema']};")
        
        #4. Create File Format for CSV
        curr.execute("""
            CREATE OR REPLACE FILE FORMAT csv_ingest_format
            TYPE = CSV
            PARSE_HEADER = TRUE
            FIELD_DELIMITER = ','
            FIELD_OPTIONALLY_ENCLOSED_BY = '"'
        """)
        
        # 5. Create a Temporary Stage to access S3 (Equivalent to DuckDB Create Secret)
        curr.execute(f"""
            CREATE OR REPLACE TEMPORARY STAGE nppes_s3_stage
            URL = 's3://{aws_bucket}/{aws_team_folder}/'
            CREDENTIALS = (
                AWS_KEY_ID = '{aws_credentials.access_key}',
                AWS_SECRET_KEY = '{aws_credentials.secret_key}',
                AWS_TOKEN = '{aws_credentials.token}'
            )
        """)

        # 6. Define File Map
        files = {
            # "npi_data": {"path": npi_csv_file, "type": "csv"},
            "nucc_taxonomy": {"path": nucc_taxonomy_file, "type": "csv"},
            "nppes_sample": {"path": nppes_sample_file, "type": "csv"},
            "ssa_fips_state_county": {"path": ssa_fips_state_county_file, "type": "csv"},
            "zip_data": {"path": zip_csv_file, "type": "excel"},
            "api_data": {"path": api_csv_file, "type": "csv"}
        }

        # 7. Main Ingestion Loop
        for table_name, file_info in files.items():
            start_time = time.time()
            table_name = table_name.upper()

            try:
                if file_info["type"] == "csv":
                    logger.info(f"Native SQL Load: {table_name}")
                    
                    # Infer schema and create table
                    curr.execute(f"""
                        CREATE OR REPLACE TABLE {table_name}
                        USING TEMPLATE (
                            SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*))
                            FROM TABLE(INFER_SCHEMA(
                                LOCATION=>'@nppes_s3_stage/{file_info['path']}',
                                FILE_FORMAT=>'csv_ingest_format'
                            ))
                        );
                    """)
                    
                    # Load data
                    curr.execute(f"COPY INTO {table_name} FROM @nppes_s3_stage/{file_info['path']} FILE_FORMAT=(FORMAT_NAME='csv_ingest_format') MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE ON_ERROR='CONTINUE';")

                elif file_info["type"] == "excel":
                    logger.info(f"Polars ADBC Load: {table_name}")
                    
                    # Download and read with Polars
                    s3_client = aws_session.client('s3')
                    obj = s3_client.get_object(Bucket=aws_bucket, Key=f"{aws_team_folder}/{file_info['path']}")
                    
                    df_placeholder = pl.read_excel(BytesIO(obj['Body'].read()), engine="calamine")
                    
                    # Clean columns (Upper case, no spaces)
                    df_placeholder = df_placeholder.rename({c: c.upper().replace(" ", "_") for c in df_placeholder.columns})

                    # Connection string for ADBC
                    adbc_url = f"snowflake://{snowflake_config['user']}:{snowflake_config['password']}@{snowflake_config['account']}/{snowflake_config['database']}/{snowflake_config['schema']}?warehouse={snowflake_config['warehouse']}"
                    
                    df_placeholder.write_database(
                        table_name=table_name,
                        connection=adbc_url,
                        engine="adbc",
                        if_table_exists="replace"
                    )

                duration = round((time.time() - start_time) / 60, 2)
                logger.info(f"{table_name} finished in {duration} mins.")
                
            except Exception as e:
                logger.error(f"Error on {table_name}: {str(e)}")
    
    except Exception as e:  
        logger.error(f"Critical Error: {e}", exc_info=True)

    finally:
        curr.close()
        conn.close()

        # 6. Main Ingestion Loop
        # for table_name, file_info in files.items():
        #     start_time = time.time()
        #     s3_path = f"s3://{aws_bucket}/{aws_team_folder}/{file_info['path']}"
        #     s3_key = f"{aws_team_folder}/{file_info['path']}"
            
        #     # Check if table already exists to skip re-downloading
        #     table_exists = duck_conn.execute(f"SELECT count(*) FROM information_schema.tables WHERE table_name = '{table_name}'").fetchone()[0]
        #     if table_exists > 0:
        #         logger.info(f"Table {table_name} already exists. Skipping...")
        #         continue
            
        #     try:
        #         large_file = is_large_file(aws_session, aws_bucket, s3_key)
                
        #         if file_info["type"] == "csv" and large_file:
        #             logger.info(f"Starting Large Ingestion: {table_name}...")
        #             duck_conn.execute(f"""
        #                 CREATE OR REPLACE TABLE raw.{table_name} AS
        #                 SELECT * FROM read_csv_auto('{s3_path}', header=TRUE, parallel=TRUE, ALL_VARCHAR=TRUE, QUOTE='\"', IGNORE_ERRORS=TRUE)
        #             """)
        #         elif file_info["type"] == "excel":
        #             logger.info(f"Reading Excel: {table_name}...")
        #             # response = aws_s3_client.get_object(Bucket=aws_bucket, Key=s3_key)
        #             # excel_data = response['Body'].read()
        #             # raw_data = pl.read_excel(BytesIO(excel_data))
        #             # duck_conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM raw_data")
        #             duck_conn.execute(f"""CREATE OR REPLACE TABLE raw.{table_name} AS SELECT * FROM read_xlsx('{s3_path}')""")
        #         elif file_info["type"] == "csv":
        #             logger.info(f"Reading small CSV: {table_name}...")
        #             duck_conn.execute(f"CREATE OR REPLACE TABLE raw.{table_name} AS SELECT * FROM read_csv_auto('{s3_path}')")

        #         duration = round((time.time() - start_time) / 60, 2)
        #         logger.info(f" {table_name} completed in {duration} minutes.")

        #     except Exception as path_err:
        #         logger.error(f"Error processing {table_name}: {path_err}")
        #         continue

        logger.info(" All data loaded successfully.")
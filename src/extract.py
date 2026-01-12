from io import BytesIO
import os
import csv
from dotenv import load_dotenv
import polars as pl
import duckdb
import boto3


from local_logging import get_logger

logger = get_logger("extract")

load_dotenv()

aws_sso_profile_name = os.getenv("sso_profile_name")
aws_region_name = os.getenv("AWS_REGION_NAME")
aws_bucket = os.getenv("aws_bucket_name")
aws_team_folder = os.getenv("team_folder")
aws_sso_profile_name = os.getenv("sso_profile_name")
aws_session = boto3.Session(profile_name=os.getenv("sso_profile_name"))
aws_s3_client = aws_session.client('s3')

npi_csv_file = os.getenv("npi_csv_data")
nucc_taxonomy_file = os.getenv("nucc_taxonomy")
nppes_sample_file = os.getenv("nppes_sample")
ssa_fips_state_county_file = os.getenv("ssa_fips_state_county")
zip_csv_file = os.getenv("zip_csv")

LARGE_FILE_THRESHOLD_GB = 2
CHUNK_SIZE = 500_000

def is_large_file(aws_session,aws_bucket, s3_key, threshold_gb=LARGE_FILE_THRESHOLD_GB):
    s3 = aws_session.client('s3')
    size = s3.head_object(Bucket=aws_bucket, Key=s3_key)['ContentLength']
    size_gb = size / (1024 ** 3)
    return size_gb > threshold_gb

def ingestion_data_into_duckdb(aws_session):
    
    try:
        aws_credentials = aws_session.get_credentials().get_frozen_credentials()

        with duckdb.connect("NPPES.duckdb") as duck_conn:  
            duck_conn.execute("INSTALL aws;")
            duck_conn.execute("LOAD aws;")
            duck_conn.execute(f"SET s3_access_key_id = '{aws_credentials.access_key}';")
            duck_conn.execute(f"SET s3_secret_access_key = '{aws_credentials.secret_key}';")
            duck_conn.execute(f"SET s3_session_token = '{aws_credentials.token}';")
            duck_conn.execute(f"SET s3_region = '{aws_region_name}';")
            files = {
              "npi_data": {"path": npi_csv_file, "type": "csv"},
              "nucc_taxonomy": {"path": nucc_taxonomy_file, "type": "csv"},
              "nppes_sample": {"path": nppes_sample_file, "type": "csv"},
              "ssa_fips_state_county": {"path": ssa_fips_state_county_file, "type": "csv"},
              "zip_data": {"path": zip_csv_file, "type": "excel"}
             }

        
            for table_name, file_info in files.items():
             s3_path = f"s3://{aws_bucket}/{aws_team_folder}/{file_info['path']}"
             s3_key = f"{aws_team_folder}/{file_info['path']}"

             if file_info["type"] == "csv" and is_large_file(aws_session,aws_bucket, s3_key):
                logger.info(f"Large CSV file detected: {s3_path}. Ingesting in chunks...")
                # ingest_large_csv_polars_lazy(
                #         s3_client=aws_s3_client,
                #         aws_bucket=aws_bucket,
                #         s3_key=s3_key,
                #         table_name=table_name,
                #         duck_conn=duck_conn
                #     )
                # continue
                duck_conn.execute("PRAGMA threads=8;")
                duck_conn.execute(f"""
                              CREATE OR REPLACE TABLE npi_data AS
                                      SELECT *
                                    FROM read_csv_auto('{s3_path}', ALL_VARCHAR=TRUE, SAMPLE_SIZE=100_000)
                               """)

                logger.info("NPI CSV ingestion completed successfully!")


             elif file_info["type"] == "excel":
                logger.info(f"csv file detected: {s3_path}. Reading with Polars...")
                raw_data = pl.read_excel(s3_path)
                duck_conn.register("temp_table", raw_data)
                duck_conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM temp_table")
                logger.info(f"Excel data ingested into DuckDB table: {table_name} from {s3_path}")

             elif file_info["type"] == "csv":
                logger.info(f"CSV file detected: {s3_path}. Reading with Polars...")
                raw_data = pl.scan_csv(s3_path,infer_schema_length=10_000)
                duck_conn.register("temp_table", raw_data)
                duck_conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM temp_table")
                logger.info(f"Data ingested into DuckDB table: {table_name} from {s3_path}")

             else:
                raise ValueError(f"Unsupported file type: {file_info['type']}")
            
        logger.info("All data ingestion completed successfully.")



    except Exception as e:  
        logger.error(f"Error in from_s3_to_duckdb: {e}",exc_info=True)

def zip_pop_from_api():
    base_url = census_api_url
    params = {
        "get": "DP05_0001E",
        "for": "zip code tabulation area:*",
        "key": census_api_key}
    query_string = urlencode(params, quote_via=quote)
    query_string = query_string.replace('%2A', '*')
    query_string = query_string.replace('%3A', ':')
    full_url = f"{base_url}?{query_string}"
    # full_url_for_debugging = "https://api.census.gov/data/2023/acs/acs5/profile?get=DP05_0001E&for=zip%20code%20tabulation%20area:*&key=dc742cafb6c2202034b1be943e5fcf02e2e744a9"

    try:
        response = requests.get(full_url)
        response.raise_for_status()
        data = response.json()
        zip_pop_df = pl.DataFrame(data[1:], schema=data[0])
        zip_pop_df = zip_pop_df.rename({"DP05_0001E": "total_population", "zip code tabulation area": "zip_code"})
        print(zip_pop_df.head())
        return zip_pop_df
    except Exception as e:
        logger.error(f"Error in zip_pop_from_api: {e}")
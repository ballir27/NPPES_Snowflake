import os
from dotenv import load_dotenv
import polars as pl
import duckdb

from local_logging import get_logger

logger = get_logger()
load_dotenv()

aws_sso_profile_name = os.getenv("sso_profile_name")
aws_region_name = os.getenv("AWS_REGION_NAME")
aws_bucket = os.getenv("aws_bucket_name")
aws_team_folder = os.getenv("team_folder")

def from_s3_to_duckdb(aws_session):
    duck_conn = duckdb.connect("words_database.duckdb")
    duck_conn.execute("INSTALL aws;")
    duck_conn.execute("LOAD aws;")
    
    try:
        #sso login
        aws_credentials = aws_session.get_credentials().get_frozen_credentials()        
        aws_access_key = aws_credentials.access_key
        aws_secret_key = aws_credentials.secret_key
        aws_session_token = aws_credentials.token        

        duck_conn.execute(f"SET s3_access_key_id = '{aws_access_key}';")
        duck_conn.execute(f"SET s3_secret_access_key = '{aws_secret_key}';")
        duck_conn.execute(f"SET s3_session_token = '{aws_session_token}';")
        duck_conn.execute(f"SET s3_region = '{aws_region_name}';")

        taxonomy_raw = duck_conn.execute(f"SELECT * FROM read_csv_auto('s3://{aws_bucket}/{aws_team_folder}/nucc_taxonomy_250.csv');").pl()
        print(taxonomy_raw.head())
    except Exception as e:
        logger.error(f"Error in from_s3_to_duckdb: {e}")
        return None
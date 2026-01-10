import os
from dotenv import load_dotenv
import polars as pl
import duckdb
import requests
from urllib.parse import urlencode, quote

from local_logging import get_logger

logger = get_logger()
load_dotenv()

aws_sso_profile_name = os.getenv("sso_profile_name")
aws_region_name = os.getenv("AWS_REGION_NAME")
aws_bucket = os.getenv("aws_bucket_name")
aws_team_folder = os.getenv("team_folder")
taxonomy_file = os.getenv("taxonomy_file")

census_api_url = os.getenv("census_api_url")
census_api_key = os.getenv("census_api_key")

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
        
        duck_conn.execute(f"CREATE SCHEMA IF NOT EXISTS raw;")

        taxonomy_raw = duck_conn.execute(f"SELECT * FROM read_csv_auto('s3://{aws_bucket}/{aws_team_folder}/{taxonomy_file}');").pl()
        print(taxonomy_raw.head())
        duck_conn.execute(f"CREATE TABLE if not exists raw.taxonomy AS SELECT * FROM read_csv_auto('s3://{aws_bucket}/{aws_team_folder}/{taxonomy_file}');")
    except Exception as e:
        logger.error(f"Error in from_s3_to_duckdb: {e}")
        return None
    
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
        return None
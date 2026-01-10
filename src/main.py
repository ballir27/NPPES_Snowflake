import polars as pl
from dotenv import load_dotenv
import os
import boto3
import duckdb

from local_logging import get_logger
import extract
import upload

logger = get_logger()
load_dotenv()

aws_sso_profile_name = os.getenv("sso_profile_name")
aws_session = boto3.Session(profile_name=os.getenv("sso_profile_name"))
aws_s3_client = aws_session.client('s3')

aws_s3_bucket = os.getenv("aws_bucket_name")
aws_team_folder = os.getenv("team_folder")

def main():
    extract.from_s3_to_duckdb(aws_session)
    zip_pop_df = extract.zip_pop_from_api()
    upload.polars_to_aws_s3(client=aws_s3_client, data=zip_pop_df, bucket=aws_s3_bucket, file_name="zip_population.csv", folder=aws_team_folder)
    

if __name__ == "__main__":
    main()
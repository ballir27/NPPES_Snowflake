import polars as pl
from dotenv import load_dotenv
import os
import boto3
import duckdb

from local_logging import get_logger
import extract

logger = get_logger()
load_dotenv()

aws_sso_profile_name = os.getenv("sso_profile_name")
aws_session = boto3.Session(profile_name=os.getenv("sso_profile_name"))
aws_s3_client = aws_session.client('s3')

def main():
    extract.from_s3_to_duckdb(aws_session)

if __name__ == "__main__":
    main()
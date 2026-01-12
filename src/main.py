import polars as pl
from dotenv import load_dotenv
import os
import boto3
import duckdb

from local_logging import get_logger
from ingestion import ingestion_data_into_duckdb

logger = get_logger("main")
load_dotenv()

aws_sso_profile_name = os.getenv("sso_profile_name")
aws_session = boto3.Session(profile_name=os.getenv("sso_profile_name"))
aws_s3_client = aws_session.client('s3')

def main():

    try:
        aws_sso_profile_name = os.getenv("sso_profile_name")

        aws_session = boto3.Session(
            profile_name=aws_sso_profile_name
        )

        logger.info("AWS session initialized successfully")

        ingestion_data_into_duckdb(aws_session)

        

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
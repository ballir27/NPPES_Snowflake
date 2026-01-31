import polars as pl
from dotenv import load_dotenv
import os
import boto3
import duckdb

from local_logging import get_logger
from ingestion import ingest_into_snowflake
import upload

logger = get_logger("main")
load_dotenv()

aws_sso_profile_name = os.getenv("sso_profile_name")
aws_session = boto3.Session(profile_name=os.getenv("sso_profile_name"))
aws_s3_client = aws_session.client('s3')

aws_s3_bucket = os.getenv("aws_bucket_name")
aws_team_folder = os.getenv("team_folder")

snowflake_account = os.getenv("snowflake_account")
snowflake_user = os.getenv("snowflake_user")
snowflake_password = os.getenv("snowflake_password")
snowflake_warehouse = os.getenv("snowflake_warehouse")
snowflake_database = os.getenv("snowflake_database")
snowflake_schema = os.getenv("snowflake_schema")
snowflake_role = os.getenv("snowflake_role")

def main():

    try:
        aws_sso_profile_name = os.getenv("sso_profile_name")

        aws_session = boto3.Session(
            profile_name=aws_sso_profile_name
        )
        
        snowflake_config = {
            "account": snowflake_account,
            "user": snowflake_user,
            "password": snowflake_password,
            "warehouse": snowflake_warehouse,      # The compute engine (must be started)
            "database": snowflake_database,         # The container for your data
            "schema": snowflake_schema,                # The namespace within the DB
            "role": snowflake_role          # Optional: Specify your security role
        }

        logger.info("AWS session initialized successfully")
        
        zip_pop_df = api_extract.zip_pop_from_api()
        upload.polars_to_aws_s3(client=aws_s3_client, data=zip_pop_df, bucket=aws_s3_bucket, file_name="zip_population.csv", folder=aws_team_folder)

        ingest_into_snowflake(aws_session, snowflake_config)    

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
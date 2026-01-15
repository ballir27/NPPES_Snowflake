from io import StringIO
from local_logging import get_logger

logger= get_logger()

def polars_to_aws_s3(client, data, bucket, file_name, folder = None):
    try:
        s3_key = f"{folder}/{file_name}"
        csv_buffer = StringIO()
        data.write_csv(csv_buffer)
        client.put_object(Bucket=bucket, Key=s3_key, Body=csv_buffer.getvalue())
        logger.info(f"File {file_name} uploaded to S3 bucket {bucket} successfully at {folder}.")

    except Exception as e:
        logger.error(f"Error uploading file to S3: {e}", exc_info=True)
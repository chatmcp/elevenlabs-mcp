import boto3
import os
from botocore.client import Config
from botocore.exceptions import NoCredentialsError


def get_s3_client():
    """Initializes and returns an S3 client."""
    access_key = os.getenv("S3_ACCESS_KEY_ID")
    secret_key = os.getenv("S3_SECRET_ACCESS_KEY")
    endpoint_url = os.getenv("S3_ENDPOINT_URL")
    region_name = os.getenv("S3_REGION")

    if not all([access_key, secret_key, endpoint_url]):
        raise ValueError(
            "S3 credentials and endpoint URL must be set in environment variables."
        )

    return boto3.client(
        "s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        endpoint_url=endpoint_url,
        region_name=region_name,
        config=Config(signature_version="s3v4"),
    )


def upload_to_s3(file_bytes, object_name, content_type):
    """
    Uploads a file to an S3-compatible storage.

    Args:
        file_bytes (bytes): The file content in bytes.
        object_name (str): The name of the object in the S3 bucket.
        content_type (str): The MIME type of the file.

    Returns:
        str: The public URL of the uploaded file.
    """
    bucket_name = os.getenv("S3_BUCKET_NAME")
    if not bucket_name:
        raise ValueError("S3_BUCKET_NAME environment variable is required.")

    s3_client = get_s3_client()

    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=object_name,
            Body=file_bytes,
            ContentType=content_type,
        )
        endpoint_url = os.getenv("S3_ENDPOINT_URL")

        # Construct the public URL
        # Some S3 providers use a different URL structure for public access.
        # This format is common, but might need adjustment for specific providers.
        # For example, for minio it is http://<endpoint>/<bucket>/<object>
        public_url = f"{endpoint_url}/{bucket_name}/{object_name}"

        return public_url

    except NoCredentialsError:
        raise ValueError("Credentials not available for S3 upload.")
    except Exception as e:
        raise RuntimeError(f"Failed to upload file to S3: {e}")

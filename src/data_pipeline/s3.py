import boto3
import os
from botocore.exceptions import NoCredentialsError, PartialCredentialsError


def upload_file(file_path, bucket_name, object_name):
    """
    Upload a file to a specified S3 bucket.

    :param file_path: The local file path to upload.
    :param bucket_name: The name of the S3 bucket.
    :param object_name: The name of the object in the S3 bucket.
    :return: None
    """
    s3_client = boto3.client("s3")

    try:
        s3_client.upload_file(file_path, bucket_name, object_name)
        print(f"File uploaded successfully to s3://{bucket_name}/{object_name}")
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
    except NoCredentialsError:
        print("Error: AWS credentials not available.")
    except PartialCredentialsError:
        print("Error: Incomplete AWS credentials provided.")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")


def fetch_file(file_path, bucket_name, object_name):
    """
    Fetch a file: if it exists locally, return its path. Otherwise, download it from S3.

    :param file_path: The local file path to check or save the downloaded file.
    :param bucket_name: The name of the S3 bucket.
    :param object_name: The name of the object in the S3 bucket.
    :return: The file path (consumer handles parsing).
    """
    if os.path.exists(file_path):
        print(f"File already exists locally: {file_path}")
        return file_path  # Consumer handles parsing

    s3_client = boto3.client("s3")
    try:
        s3_client.download_file(bucket_name, object_name, file_path)
        print(f"File downloaded from s3://{bucket_name}/{object_name} → {file_path}")
        return file_path  # Consumer handles parsing

    except FileNotFoundError:
        print(f"Error: Invalid file path {file_path}.")
    except NoCredentialsError:
        print("Error: AWS credentials not available.")
    except PartialCredentialsError:
        print("Error: Incomplete AWS credentials provided.")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")

    return None  # Indicate failure

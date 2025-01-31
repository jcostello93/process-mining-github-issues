import boto3
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
        # Upload the file to S3
        s3_client.upload_file(file_path, bucket_name, object_name)
        print(f"File uploaded successfully to s3://{bucket_name}/{object_name}")

    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
    except NoCredentialsError:
        print("Credentials not available.")
    except PartialCredentialsError:
        print("Incomplete credentials provided.")
    except Exception as e:
        print(f"An error occurred: {e}")

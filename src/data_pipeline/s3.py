import json
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import os


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


def get_json_from_file(file_path):
    """
    Load a JSON file and return its content as a dictionary.

    :param file_path: The local file path to the JSON file.
    :return: A dictionary with the JSON content.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON file {file_path}: {e}")
        return None
    except Exception as e:
        print(f"An error occurred while reading {file_path}: {e}")
        return None


def get_file(file_path, bucket_name, object_name):
    """
    Check if a file exists locally, and if not, download it from a specified S3 bucket,
    save it locally, and return its content as a dictionary.

    :param file_path: The local file path to save the downloaded file.
    :param bucket_name: The name of the S3 bucket.
    :param object_name: The name of the object in the S3 bucket.
    :return: A dictionary with the JSON content of the file.
    """
    if os.path.exists(file_path):
        print(f"File already exists locally: {file_path}")
        return get_json_from_file(file_path)

    s3_client = boto3.client("s3")

    try:
        s3_client.download_file(bucket_name, object_name, file_path)
        print(
            f"File downloaded successfully from s3://{bucket_name}/{object_name} to {file_path}"
        )
        return get_json_from_file(file_path)

    except FileNotFoundError:
        print(f"The file path {file_path} is invalid.")
        return None
    except NoCredentialsError:
        print("Credentials not available.")
        return None
    except PartialCredentialsError:
        print("Incomplete credentials provided.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

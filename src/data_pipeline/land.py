import argparse
import os
from src.data_pipeline.s3 import upload_file

S3_BUCKET = os.environ.get("S3_BUCKET")


def main(owner, repo, domain):
    file_name = f"{owner}_{repo}_{domain}.json"
    file_path = os.path.join(os.getcwd(), file_name)
    bucket_name = S3_BUCKET
    object_name = file_name

    print("Uploading file to S3")
    upload_file(file_path, bucket_name, object_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Land raw data in S3")
    parser.add_argument("--owner", required=True, help="Owner of the repository")
    parser.add_argument("--repo", required=True, help="Repository name")
    parser.add_argument("--domain", required=True, help="Domain information")
    args = parser.parse_args()
    owner, repo, domain = args.owner, args.repo, args.domain

    main(owner, repo, domain)

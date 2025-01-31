import argparse
import os
import json
from src.data_pipeline.github import fetch_all_issues, fetch_timeline
from src.data_pipeline.s3 import fetch_file

S3_BUCKET = os.environ.get("S3_BUCKET")


def fetch_all_timelines(owner, repo):
    issues_file_name = f"{owner}_{repo}_issues.json"
    file_path = os.path.join(os.getcwd(), issues_file_name)
    bucket_name = S3_BUCKET
    object_name = issues_file_name

    print("Retrieving issues from S3")
    issues = fetch_file(file_path, bucket_name, object_name)
    with open(issues_file_name, "r", encoding="utf-8") as file:
        issues = json.load(file)
    timelines = {}
    for issue in issues:
        issue_number = issue["number"]
        print(f"Fetching timeline for issue #{issue_number}...")
        timelines[issue_number] = fetch_timeline(issue_number, owner, repo)
    return timelines


def get_domain_data(owner, repo, domain):
    data = {}
    if domain == "issues":
        data = fetch_all_issues(owner, repo)
    elif domain == "timelines":
        data = fetch_all_timelines(owner, repo)

    return data


def main(owner, repo, domain):
    print(f"Extracting {owner}, {repo}, {domain}")
    data = get_domain_data(owner, repo, domain)
    file_name = f"{owner}_{repo}_{domain}.json"
    print(f"Writing {file_name} to file")
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Land raw data in S3")
    parser.add_argument("--owner", required=True, help="Owner of the repository")
    parser.add_argument("--repo", required=True, help="Repository name")
    parser.add_argument("--domain", required=True, help="Domain information")
    args = parser.parse_args()
    owner, repo, domain = args.owner, args.repo, args.domain

    main(owner, repo, domain)

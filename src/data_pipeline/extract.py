import argparse
import json
from src.data_pipeline.github import fetch_all_issues


def get_domain_data(owner, repo, domain):
    data = {}
    if domain == "issues":
        data = fetch_all_issues(owner, repo)

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

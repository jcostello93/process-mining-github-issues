import argparse
from src.data_pipeline import extract, land, transform


def extract_and_land_domain(owner, repo, domain):
    print(f"Extract and land: {domain}")
    extract.main(owner, repo, domain)
    land.main(owner, repo, domain)


def main(owner, repo, should_publish):
    print("Running full ELT pipeline")
    extract_and_land_domain(owner, repo, "issues")
    extract_and_land_domain(owner, repo, "timelines")

    print("Transform")
    transform.main(owner, repo, should_publish)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Land raw data in S3")
    parser.add_argument("--owner", required=True, help="Owner of the repository")
    parser.add_argument("--repo", required=True, help="Repository name")
    parser.add_argument("--publish", action="store_true", help="Publish the data")
    args = parser.parse_args()
    owner, repo, should_publish = args.owner, args.repo, args.publish
    main(owner, repo, should_publish)

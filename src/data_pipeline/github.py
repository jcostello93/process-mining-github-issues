import requests
import os
import time

GITHUB_TOKEN = os.getenv("GH_PAT")
BASE_URL = "https://api.github.com/repos"
MAX_PAGES = 100
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}


def fetch_all_pages(
    url, params=None, timeout=10, max_retries=3, custom_headers=None, wait=0.7
):
    results = []
    retries = 0
    headers = HEADERS.copy()
    if custom_headers:
        headers.update(custom_headers)
    while url:
        try:
            response = requests.get(
                url, headers=headers, params=params, timeout=timeout
            )
            if response.status_code != 200:
                print(f"Failed to fetch data: {response.json()}")
                break
            data = response.json()
            results.extend(data)
            url = response.links.get("next", {}).get("url")

            # Stay under GitHub's 5,000 req/hour rate limit
            # https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api
            if wait:
                time.sleep(wait)

            rate_limit_remaining = response.headers.get("X-RateLimit-Remaining")
            rate_limit_reset = response.headers.get("X-RateLimit-Reset")
            print(f"Rate Limit Remaining: {rate_limit_remaining}")
            if rate_limit_remaining == "0":
                reset_time = int(rate_limit_reset) - int(time.time())
                print(f"Rate limit exceeded. Sleeping for {reset_time + 1} seconds.")
                time.sleep(reset_time + 1)

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            retries += 1
            if retries >= max_retries:
                print("Max retries reached. Exiting.")
                break
            print(f"Retrying... ({retries}/{max_retries})")
            time.sleep(2**retries)
    return results


def fetch_all_issues(owner, repo):
    url = f"{BASE_URL}/{owner}/{repo}/issues"
    params = {"state": "all", "per_page": MAX_PAGES}
    issues_and_pull_requests = fetch_all_pages(url, params)
    return [item for item in issues_and_pull_requests if "pull_request" not in item]


# Fetch the timeline for a specific issue
def fetch_timeline(issue_number, owner, repo):
    url = f"{BASE_URL}/{owner}/{repo}/issues/{issue_number}/timeline"
    custom_headers = {"Accept": "application/vnd.github.mockingbird-preview+json"}
    return fetch_all_pages(url, custom_headers=custom_headers)

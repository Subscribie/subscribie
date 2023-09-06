import os
import requests
from datetime import datetime, timedelta
import subprocess

# Get the current datetime
current_datetime = datetime.now()
# DOKKU_HOST
DOKKU_HOST = os.environ["DOKKU_HOST"]
# Fetch all open pull requests
url = "https://api.github.com/repos/subscribie/subscribie/pulls?state=open"
response = requests.get(url)
pull_requests = response.json()

# Iterate through the open pull requests
for pull_request in pull_requests:
    pull_request_number = pull_request["number"]

    # Fetch the commits for the pull request
    commits_url = pull_request["commits_url"].replace("{/sha}", "")
    response = requests.get(commits_url)
    commits = response.json()

    # Extract the commit dates
    commit_dates = [commit["commit"]["committer"]["date"] for commit in commits]

    # Calculate the age
    most_recent_commit_date = max(commit_dates)
    most_recent_commit_datetime = datetime.strptime(
        most_recent_commit_date, "%Y-%m-%dT%H:%M:%SZ"
    )
    current_datetime = datetime.now()
    age = current_datetime - most_recent_commit_datetime
    print(f"Pull Request #{pull_request_number} is {age} days old.")

    if age >= timedelta(days=3):
        head_ref = pull_request["head"]["ref"]
        find_hyphen = head_ref.rfind("-")
        head_ref = head_ref[:60].lower()
        container_name = head_ref[:find_hyphen] + head_ref[find_hyphen + 1 :]
        print(
            f"Pull Request #{pull_request_number} has a commit older than 3 days. Head ref: {head_ref}"
        )
        subprocess.run(
            f'ssh dokku@{ DOKKU_HOST } -C "dokku -- --force apps:destroy { container_name }" ',
            shell=True,
        )
    else:
        print("no inactive pr-preview found")

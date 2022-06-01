# this file is necessary for legacy integrations

import requests
from typing import Union, Tuple
from cli import sca, version

class GithubVersionChecker:
    GITHUB_LATEST_RELEASE_URL = "https://api.github.com/repos/soos-io/soos-ci-analysis-python/releases/latest"
    VERSION_KEY = "tag_name"
    URL_KEY = "html_url"

    @staticmethod
    def get_latest_version() -> Union[Tuple[str, str], None]:
        try:
            headers = {'Accept': 'application/vnd.github.v3+json'}
            github_release_response: requests.Response = requests.get(
                url=GithubVersionChecker.GITHUB_LATEST_RELEASE_URL,
                headers=headers)
            if github_release_response.ok:
                json_response = github_release_response.json()
                version = json_response[
                    GithubVersionChecker.VERSION_KEY] if GithubVersionChecker.VERSION_KEY in json_response else None
                url = json_response[
                    GithubVersionChecker.URL_KEY] if GithubVersionChecker.URL_KEY in json_response else None

                return version, url
            else:
                return None
        except Exception as e:
            return None

print(__name__)
if __name__ == "__main__":
    sca.SOOS.console_log("Checking Script Version.....")
    latest_version, github_url = GithubVersionChecker.get_latest_version()
    current_version = f"v{version.get_current_version()}"

#   if latest_version is not None and latest_version != current_version:
#     sca.SOOS.console_log(
#         f"Your current version {current_version} is outdated. The latest version available is {latest_version}. Please update to the latest version here: {github_url}")
#   else:
#     sca.SOOS.console_log(f"Your current version {current_version} is the latest version available")

    sca.entry_point()

import argparse
import base64
import fnmatch
import glob
import gzip
import json
import os
import platform
import sys
import time
import requests
from datetime import datetime
from pathlib import Path, WindowsPath, PurePath, PureWindowsPath  # User Home Folder references
from typing import List, AnyStr, Optional, Any, Dict, Union, Tuple


SCAN_TYPE = "sca"
ANALYSIS_START_TIME = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
MAX_MANIFESTS = 50
SCAN_STATUS_ERROR = "Error"
SCAN_STATUS_INCOMPLETE = "Incomplete"

with open(os.path.join(os.path.dirname(__file__), "VERSION.txt")) as version_file:
  SCRIPT_VERSION = version_file.read().strip()

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


class ErrorAPIResponse:
    code: Optional[str] = None
    message: Optional[str] = None

    def __init__(self, api_response):
        for key in api_response:
            self.__setattr__(key, api_response[key])

        self.code = api_response["code"] if "code" in api_response else None
        self.message = api_response["message"] if "message" in api_response else None


class SOOSStructureAPIResponse:

    def __init__(self, structure_response_api):
        self.original_response = structure_response_api

        self.content_object = None

        self.structure_id = None
        self.project_id = None
        self.analysis_id = None
        self.report_url = None
        self.embed_url = None
        self.report_status_url = None

        if self.original_response is not None:
            self.content_object = json.loads(self.original_response.content)

            self.structure_id = self.content_object["Id"] if "Id" in self.content_object else None
            self.project_id = self.content_object["projectId"] if "projectId" in self.content_object else None
            self.analysis_id = self.content_object["Id"] if "Id" in self.content_object else None
            self.report_url = self.content_object["reportUrl"] if "reportUrl" in self.content_object else None
            self.embed_url = self.content_object["embedUrl"] if "embedUrl" in self.content_object else None
            self.report_status_url = self.content_object[
                "reportStatusUrl"] if "reportStatusUrl" in self.content_object else None


class CreateScanAPIResponse:
    clientHash: Optional[str] = None
    projectHash: Optional[str] = None
    branchHash: Optional[str] = None
    analysisId: Optional[str] = None
    scanType: Optional[int] = None
    scanUrl: Optional[str] = None
    scanStatusUrl: Optional[str] = None
    errors: Optional[List[Any]] = None

    def __init__(self, create_scan_json_response):
        for key in create_scan_json_response:
            self.__setattr__(key, create_scan_json_response[key])

class Manifest:
    name: Optional[str] = None
    filename: Optional[str] = None
    packageManager: Optional[str] = None
    status: Optional[str] = None
    statusMessage: Optional[str] = None

    def __init__(self, manifest_json):
        for key in manifest_json:
            self.__setattr__(key, manifest_json[key])

class AddManifestsResponse:
    code: Optional[str] = None
    message: Optional[str] = None
    statusCode: Optional[int] = None
    projectId: Optional[str] = None
    analysisId: Optional[str] = None
    validManifestCount: Optional[int] = None
    invalidManifestCount: Optional[int] = None
    manifests: Optional[List[Manifest]] = None

    def __init__(self, add_manifests_response_json):
        for key in add_manifests_response_json:
            if key != "manifests":
                self.__setattr__(key, add_manifests_response_json[key])
            elif add_manifests_response_json[key] is not None:
                manifests = []
                for manifest_json in add_manifests_response_json[key]:
                    manifests.append(Manifest(manifest_json))
                self.__setattr__("manifests", manifests)

class ScanStatusAPIResponse:
    status: Optional[str] = None
    analysisId: Optional[str] = None
    results: Optional[Any] = None

    def __init__(self, scan_status_json_response: Any):
        for key in scan_status_json_response:
            self.__setattr__(key, scan_status_json_response[key])


def set_body_value(body: Dict, name: str, value: Any):
    if value is not None:
        body[name] = value


def handle_response(api_response: requests.Response):
    if api_response.status_code in range(400, 600):
        return ErrorAPIResponse(api_response.json())
    else:
        if api_response.reason == "No Content":
            return None
        else:
            return api_response.json()


def handle_error(error: ErrorAPIResponse, api: str, attempt: int, max_retry: int):
    error_message = f"{api} has an error. Attempt {str(attempt)} of {str(max_retry)}"
    raise Exception(f"{error_message}\n{error.code}-{error.message}")


def generate_header(api_key: str, content_type: str):
    return {'x-soos-apikey': api_key, 'Content-Type': content_type}


def raise_max_retry_exception(attempt: int, retry_count: int):
    if attempt >= retry_count:
        raise Exception("The maximum retries allowed were reached")


class SOOSStructureAPI:
    API_RETRY_COUNT = 3

    URI_TEMPLATE = "{soos_base_uri}clients/{soos_client_id}/analysis/structure"

    def __init__(self):
        pass

    @staticmethod
    def generate_api_url(soos_context):
        url = SOOSStructureAPI.URI_TEMPLATE
        url = url.replace("{soos_base_uri}", soos_context.base_uri)
        url = url.replace("{soos_client_id}", soos_context.client_id)

        return url

    @staticmethod
    def exec(soos_context):

        api_url = SOOSStructureAPI.generate_api_url(soos_context)

        api_response = None

        structure_api_data = {
            "projectName": soos_context.project_name,
            "name": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
            "integrationType": soos_context.integration_type,
            "scriptVersion": SCRIPT_VERSION
        }

        if soos_context.branch_uri is not None:
            structure_api_data["branchUri"] = soos_context.branch_uri

        if soos_context.branch_name is not None:
            structure_api_data["branch"] = soos_context.branch_name

        if soos_context.commit_hash is not None:
            structure_api_data["commitHash"] = soos_context.commit_hash

        if soos_context.build_version is not None:
            structure_api_data["buildVersion"] = soos_context.build_version

        if soos_context.build_uri is not None:
            structure_api_data["buildUri"] = soos_context.build_uri

        if soos_context.operating_environment is not None:
            structure_api_data["operatingEnvironment"] = soos_context.operating_environment

        if soos_context.integration_name is not None:
            structure_api_data["integrationName"] = soos_context.integration_name

        if soos_context.integration_type is not None:
            structure_api_data["integrationType"] = soos_context.integration_type

        if soos_context.app_version is not None:
            structure_api_data["appVersion"] = soos_context.app_version

        for i in range(0, SOOSStructureAPI.API_RETRY_COUNT):
            try:
                kernel = requests.post(
                    url=api_url,
                    data=json.dumps(structure_api_data),
                    # files=structure_api_data,
                    headers={'x-soos-apikey': soos_context.api_key, 'Content-Type': 'application/json'})

                json_response = handle_response(api_response=kernel)

                if type(json_response) is ErrorAPIResponse:
                    api_response = json_response
                    raise Exception(f"{json_response.code}-{json_response.message}")
                else:
                    api_response = SOOSStructureAPIResponse(json_response)
                break

            except Exception as e:
                SOOS.console_log("A Structure API Exception Occurred. "
                                 "Attempt " + str(i + 1) + " of " + str(SOOSStructureAPI.API_RETRY_COUNT) + "::" +
                                 "Data: " + str(structure_api_data) + "::" +
                                 "Exception: " + str(e)
                                 )

        return api_response


class SOOSContext:

    def __init__(self):
        self.base_uri = None
        self.source_code_path = None
        self.project_name = None
        self.client_id = None
        self.api_key = None
        self.verbose_logging = False

        # Special Context - loads from script arguments only
        self.commit_hash = None
        self.branch_name = None
        self.branch_uri = None
        self.build_version = None
        self.build_uri = None
        self.operating_environment = None
        self.app_version = None
        self.integration_name = None
        self.integration_type = "Script"
        self.generate_sarif_report = False
        self.github_pat = None

    def __set_source_code_path__(self, source_code_directory):
        """
        This method receives the source code path passed as argument or env variable.
        It is used to set the source_code_path property from SOOSContext class.
        """
        plt = platform.system().lower()
        if plt == 'windows':
            path_resolver = WindowsPath
        else:
            path_resolver = Path
        if source_code_directory is not None:
            source_dir_path = path_resolver(source_code_directory)
            if not source_dir_path.is_dir() or not source_dir_path.exists():
                SOOS.console_log('ERROR: The source code directory does not exist or it is not a directory')
                sys.exit(1)

            if source_code_directory.startswith("~/") or \
                    source_code_directory.startswith("$HOME/") or \
                    source_code_directory.find("%userprofile%/"):
                self.source_code_path = str(source_dir_path.expanduser().resolve())
            else:
                self.source_code_path = str(source_dir_path.resolve())

        else:
            # FAllBACK - COULD RESULT IN ERROR DEPENDING ON MODE DESIRED
            self.source_code_path = SOOS.get_current_directory()

    def reset(self):
        self.base_uri = None
        self.source_code_path = None
        self.project_name = None
        self.client_id = None
        self.api_key = None

    def load(self, script_args):

        # Prioritize context from environment variables
        # Any environment variables that are not set will
        # automatically be searched in the script arguments
        self.load_from_env_var()

        if not self.is_valid():

            # Attempt to get MISSING context from parameters
            self.load_from_parameters(script_args=script_args)

            if not self.is_valid():
                return False

        return True

    def load_from_env_var(self):

        self.reset()

        try:
            if self.base_uri is None:
                self.base_uri = os.environ["SOOS_API_BASE_URI"]
                SOOS.console_log("SOOS_API_BASE_URI Environment Variable Loaded: " + self.base_uri)
        except Exception as e:
            pass

        try:
            if self.source_code_path is None:
                self.__set_source_code_path__(os.environ['SOOS_ROOT_CODE_PATH'])
                SOOS.console_log("SOOS_ROOT_CODE_PATH Environment Variable Loaded: " + self.source_code_path)
        except Exception as e:
            pass

        try:
            if self.project_name is None:
                self.project_name = os.environ['SOOS_PROJECT_NAME']
                SOOS.console_log("SOOS_PROJECT_NAME Environment Variable Loaded: " + self.project_name)
        except Exception as e:
            pass

        try:
            if self.client_id is None:
                self.client_id = os.environ['SOOS_CLIENT_ID']
                SOOS.console_log("SOOS_CLIENT_ID Environment Variable Loaded: SECRET")
        except Exception as e:
            pass

        try:
            if self.api_key is None:
                self.api_key = os.environ['SOOS_API_KEY']
                SOOS.console_log("SOOS_API_KEY Environment Variable Loaded: SECRET")
        except Exception as e:
            pass

    def load_from_parameters(self, script_args):
        '''
        The parameters that are present in load_from_env_var will have a chance to be overloaded here.
        All other parameters can only be found in the args list.

        :param script_args:
        :return:
        '''

        # Do not reset - enable parameters to override environment variables
        # self.reset()

        if script_args.base_uri is not None:
            self.base_uri = str(script_args.base_uri)
            SOOS.console_log("SOOS_API_BASE_URI Parameter Loaded: " + self.base_uri)

        if script_args.source_code_path is not None:
            self.__set_source_code_path__(str(script_args.source_code_path))
            SOOS.console_log("SOOS_ROOT_CODE_PATH Parameter Loaded: " + self.source_code_path)

        if script_args.project_name is not None:
            self.project_name = str(script_args.project_name)
            SOOS.console_log("SOOS_PROJECT_NAME Parameter Loaded: " + self.project_name)

        if script_args.client_id is not None:
            self.client_id = str(script_args.client_id)
            SOOS.console_log("SOOS_CLIENT_ID Parameter Loaded: SECRET")

        if script_args.api_key is not None:
            self.api_key = str(script_args.api_key)
            SOOS.console_log("SOOS_API_KEY Parameter Loaded: SECRET")

        if script_args.logging_verbose is True or str(script_args.logging_verbosity).upper() == "DEBUG":
            self.verbose_logging = True
            SOOS.console_log("SOOS_VERBOSE_LOGGING: Enabled")

        # ##################################################
        # Special Context - loads from script arguments only
        # ##################################################

        if script_args.commit_hash is not None:
            if len(script_args.commit_hash) > 0:
                self.commit_hash = str(script_args.commit_hash)
                SOOS.console_log("SOOS_COMMIT_HASH Parameter Loaded: " + self.commit_hash)

        if script_args.branch_name is not None:
            if len(script_args.branch_name) > 0:
                self.branch_name = str(script_args.branch_name)
                SOOS.console_log("SOOS_BRANCH_NAME Parameter Loaded: " + self.branch_name)

        if script_args.branch_uri is not None:
            if len(script_args.branch_uri) > 0:
                self.branch_uri = str(script_args.branch_uri)
                SOOS.console_log("SOOS_BRANCH_URI Parameter Loaded: " + self.branch_uri)

        if script_args.build_version is not None:
            if len(script_args.build_version) > 0:
                self.build_version = str(script_args.build_version)
                SOOS.console_log("SOOS_BUILD_VERSION Parameter Loaded: " + self.build_version)

        if script_args.build_uri is not None:
            if len(script_args.build_uri) > 0:
                self.build_uri = str(script_args.build_uri)
                SOOS.console_log("SOOS_BUILD_URI Parameter Loaded: " + self.build_uri)

        # Operating environment, if missing, will default to platform

        if script_args.operating_environment is not None and len(script_args.operating_environment) > 0:
            self.operating_environment = str(script_args.operating_environment)
        else:
            self.operating_environment = '{system} {release} {architecture}'.format(system=platform.system(), release=platform.release(), architecture=platform.architecture()[0])
        SOOS.console_log("SOOS_OPERATING_ENVIRONMENT Parameter Loaded: " + self.operating_environment)

        if script_args.app_version is not None and len(script_args.app_version) > 0:
            self.app_version = str(script_args.app_version)
            SOOS.console_log("SOOS_APP_VERSION Parameter Loaded: " + self.app_version)

        if script_args.integration_name is not None and len(script_args.integration_name) > 0:
            self.integration_name = str(script_args.integration_name)
            SOOS.console_log("SOOS_INTEGRATION_NAME Parameter Loaded: " + self.integration_name)

        if script_args.integration_type is not None and len(script_args.integration_type) > 0:
            self.integration_type = str(script_args.integration_type)
            SOOS.console_log("SOOS_INTEGRATION_TYPE Parameter Loaded: " + self.integration_type)

        if script_args.generate_sarif_report is True:
            self.generate_sarif_report = script_args.generate_sarif_report
            SOOS.console_log("SOOS_GENERATE_SARIF_REPORT Parameter Loaded: " + str(self.generate_sarif_report))

        if script_args.github_pat is not None:
            self.github_pat = script_args.github_pat
            SOOS.console_log("SOOS_GITHUB_PAT Parameter Loaded: <SECRET>")

    def is_valid(self):

        if self.base_uri is None or len(self.base_uri) == 0:
            return False

        if self.source_code_path is None or len(self.source_code_path) == 0:
            return False

        if self.project_name is None or len(self.project_name) == 0:
            return False

        if self.client_id is None or len(self.client_id) == 0:
            return False

        if self.api_key is None or len(self.api_key) == 0:
            return False

        return True

    def print_invalid(self):

        if self.base_uri is None or len(self.base_uri) == 0:
            SOOS.console_log("REQUIRED PARAMETER IS MISSING: SOOS_API_BASE_URI")

        if self.source_code_path is None or len(self.source_code_path) == 0:
            SOOS.console_log("REQUIRED PARAMETER IS MISSING: SOOS_ROOT_CODE_PATH")

        if self.project_name is None or len(self.project_name) == 0:
            SOOS.console_log("REQUIRED PARAMETER IS MISSING: SOOS_PROJECT_NAME")

        if self.client_id is None or len(self.client_id) == 0:
            SOOS.console_log("REQUIRED PARAMETER IS MISSING: SOOS_CLIENT_ID")
            SOOS.console_log(
                "CLIENT_ID, found at https://app.soos.io/integrate/sca")

        if self.api_key is None or len(self.api_key) == 0:
            SOOS.console_log("REQUIRED PARAMETER IS MISSING: SOOS_API_KEY")
            SOOS.console_log(
                "API_KEY, found at https://app.soos.io/integrate/sca")


class SOOSScanAPI:
    URLS: dict = {
        "create": "{baseUri}clients/{clientHash}/scan-types/{scanType}/scans",
        "status": "{baseUri}clients/{clientHash}/projects/{projectHash}/branches/{branchHash}/scan-types/{scanType}/scans/{scanId}"
    }
    API_RETRY_COUNT = 3

    def __init__(self):
        pass

    @staticmethod
    def generate_scan_api_url(context: SOOSContext, url_type: str, **kwargs) -> str:
        if url_type not in SOOSScanAPI.URLS.keys():
            raise Exception(f"URL type invalid: {url_type}")

        params_args = {
            "baseUri": context.base_uri,
            "clientHash": context.client_id,
            "scanType": SCAN_TYPE
        }

        if url_type == 'status':
            params_args["projectHash"] = kwargs.get("projectHash")
            params_args["branchHash"] = kwargs.get("branchHash")
            params_args["scanId"] = kwargs.get("scanId")

        url = SOOSScanAPI.URLS.get(url_type).format(**params_args)

        SOOS.console_log(f"Scan URL: {url}")

        return url

    @staticmethod
    def create_scan_metadata(context: SOOSContext) -> Union[CreateScanAPIResponse, ErrorAPIResponse]:
        create_scan_response = None

        try:
            url = SOOSScanAPI.generate_scan_api_url(context=context, url_type="create")

            start_scan_data = {
                "projectName": context.project_name,
                "name": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                "integrationType": context.integration_type,
                "scriptVersion": SCRIPT_VERSION,
            }

            set_body_value(start_scan_data, 'commitHash', context.commit_hash)
            set_body_value(start_scan_data, 'branch', context.branch_name)
            set_body_value(start_scan_data, 'branchUri', context.branch_uri)
            set_body_value(start_scan_data, 'buildVersion', context.build_version)
            set_body_value(start_scan_data, 'buildUri', context.build_uri)
            set_body_value(start_scan_data, 'operatingEnvironment', context.operating_environment)
            set_body_value(start_scan_data, 'integrationName', context.integration_name)
            set_body_value(start_scan_data, 'appVersion', context.app_version)

            headers = generate_header(api_key=context.api_key, content_type="application/json")
            data = json.dumps(start_scan_data)
            attempt = 0

            for attempt in range(0, SOOSScanAPI.API_RETRY_COUNT):
                api_response: requests.Response = requests.post(url=url, data=data, headers=headers)
                json_response = handle_response(api_response)
                if type(json_response) is ErrorAPIResponse:
                    create_scan_response = json_response
                    error_message = f"A Create Scan MetaData API Exception Occurred. Attempt {str(attempt + 1)} of {str(SOOSScanAPI.API_RETRY_COUNT)}"
                    SOOS.console_log(f"{error_message}\n{json_response.code}-{json_response.message}")
                else:
                    create_scan_response = CreateScanAPIResponse(create_scan_json_response=json_response)
                    break

            raise_max_retry_exception(attempt=attempt, retry_count=SOOSScanAPI.API_RETRY_COUNT)

        except Exception as e:
            SOOS.console_log(f"ERROR: {str(e)}")

        return create_scan_response

    @staticmethod
    def get_scan_status(context: SOOSContext, **kwargs) -> Union[ScanStatusAPIResponse, ErrorAPIResponse]:
        scan_status_response = None
        projectHash = kwargs.get("projectHash")
        branchHash = kwargs.get("branchHash")
        scanId = kwargs.get("scanId")

        if projectHash is None or branchHash is None or scanId is None:
            SOOS.console_log("ERROR: projectHash, branchHash, and scanId are required")

        url = SOOSScanAPI.generate_scan_api_url(context=context, url_type="status", **kwargs)

        headers = generate_header(api_key=context.api_key, content_type="application/json")
        attempt = 0

        for attempt in range(0, SOOSScanAPI.API_RETRY_COUNT):
            try:
                api_response: requests.Response = requests.get(url=url, headers=headers)
                json_response = handle_response(api_response)
                if type(json_response) is ErrorAPIResponse:
                    scan_status_response = json_response
                    error_message = f"A Scan Status API Exception Occurred. Attempt {str(attempt + 1)} of {str(SOOSScanAPI.API_RETRY_COUNT)}"
                    SOOS.console_log(f"{error_message}\n{json_response.code}-{json_response.message}")
                else:
                    scan_status_response = ScanStatusAPIResponse(scan_status_json_response=json_response)
                    break
            except Exception as e:
                SOOS.console_log(
                    f"A Scan Status API Exception Occurred. Attempt {str(attempt + 1)} of {str(SOOSScanAPI.API_RETRY_COUNT)}")

        raise_max_retry_exception(attempt=attempt, retry_count=SOOSScanAPI.API_RETRY_COUNT)

        return scan_status_response


class SOOSManifestModel:
    filename: str
    content: any
    label: str

    def __init__(self, filename: str, label: str, content: any):
        self.filename = filename
        self.label = label
        self.content = content


class SOOSManifestAPI:
    API_RETRY_COUNT = 3

    URI_TEMPLATE = "{soos_base_uri}" \
                   "clients/{soos_client_id}" \
                   "/projects/{soos_project_id}" \
                   "/analysis/{soos_analysis_id}" \
                   "/manifests" \
                   "?hasMoreThanMaximumManifests={has_more_than_maximum_manifests}"

    def __init__(self):
        pass

    @staticmethod
    def generate_api_url(soos_context, project_id, analysis_id, has_more_than_maximum_manifests):

        api_url = SOOSManifestAPI.URI_TEMPLATE

        api_url = api_url.replace("{soos_base_uri}", soos_context.base_uri)
        api_url = api_url.replace("{soos_client_id}", soos_context.client_id)
        api_url = api_url.replace("{soos_project_id}", project_id)
        api_url = api_url.replace("{soos_analysis_id}", analysis_id)
        api_url = api_url.replace("{has_more_than_maximum_manifests}", str(has_more_than_maximum_manifests))

        return api_url

    @staticmethod
    def exec(soos_context, project_id, analysis_id, manifests, has_more_than_maximum_manifests) -> Union[
            AddManifestsResponse, ErrorAPIResponse, None]:

        api_url = SOOSManifestAPI.generate_api_url(
            soos_context, project_id, analysis_id, has_more_than_maximum_manifests
        )

        response = None

        files = []
        body = []
        for i, value in enumerate(manifests):
            suffix = i if i > 0 else ""
            files.append(("file" + str(suffix), (value.filename, value.content)))
            body.append(("parentFolder" + str(suffix), value.label))
        for i in range(0, SOOSManifestAPI.API_RETRY_COUNT):
            try:
                SOOS.console_log("*** Posting manifests to: " + api_url)
                # manifest_content is class str, convert to dict
                response = requests.post(
                    url=api_url,
                    files=dict(files),
                    data=body,
                    headers={'x-soos-apikey': soos.context.api_key,
                             },

                )

                SOOS.console_log("Manifests post Executed")
                break

            except Exception as e:
                SOOS.console_log("Manifest API Exception Occurred. "
                                 "Attempt " + str(i + 1) + " of " + str(SOOSManifestAPI.API_RETRY_COUNT))

        if response is None:
            return None

        # edge case where API returns bad response but has manifest results
        if (response.status_code == 400 and response.reason != "No Content"
                and "validManifestCount" in response.json()):
            return AddManifestsResponse(add_manifests_response_json=response.json())

        json_response = handle_response(response)
        if type(json_response) is ErrorAPIResponse:
            return json_response
        else:
            return AddManifestsResponse(add_manifests_response_json=json_response)

class SOOS:

    def __init__(self):
        self.context = SOOSContext()
        self.script = SOOSAnalysisScript()

    def load_manifest_types(self):

        MANIFEST_TEMPLATE = "{soos_base_uri}clients/{soos_client_id}/manifests"
        murl = MANIFEST_TEMPLATE
        murl = murl.replace("{soos_base_uri}", self.context.base_uri)
        murl = murl.replace("{soos_client_id}", self.context.client_id)
        my_manifests = requests.get(
            url=murl,
            headers={'x-soos-apikey': self.context.api_key, 'Content-Type': 'application/json'}
        )
        m = json.loads(my_manifests.content)
        return m

    def find_manifest_files(self, pattern: str) -> List[AnyStr]:
        manifest_glob_pattern: str = pattern
        if manifest_glob_pattern.startswith('.'):
            manifest_glob_pattern = f"*{pattern}"

        glob_pattern = f"{self.context.source_code_path}/**/{manifest_glob_pattern}"

        # on linux/unix systems, perform case-insensitive search (windows is always case-insensitive)
        plt = platform.system().lower()
        if plt != "windows":
            def case_insensitive_map(c):
                return '[%s%s]' % (c.lower(), c.upper()) if c.isalpha() else c
            glob_pattern = ''.join(map(case_insensitive_map, glob_pattern))

        return glob.glob(
            glob_pattern,
            recursive=True
        )

    # returns count of valid manifests that were uploaded or None on error
    def send_manifests(self, project_id, analysis_id, dirs_to_exclude, files_to_exclude, package_managers) -> Optional[int]:

        has_more_than_maximum_manifests = False

        code_root = SOOS.get_current_directory()

        print()
        SOOS.console_log("------------------------")
        SOOS.console_log("Begin Recursive Manifest Search")
        SOOS.console_log("------------------------")

        MANIFEST_FILES = self.load_manifest_types()
        manifestArr = []

        for manifest_file in MANIFEST_FILES:
            package_manager = manifest_file['packageManager']
            if len(package_managers) > 0 and package_manager.lower() not in (manager.lower() for manager in package_managers):
                continue
            files = []
            SOOS.console_log("Looking for " + package_manager + " files...")

            for entries in manifest_file["manifests"]:
                pattern = entries["pattern"]
                candidate_files = self.find_manifest_files(pattern=pattern)

                for cf in candidate_files:
                    files.append(cf)
            # iterate each
            # avoid directories to exclude

            for file_name in files:
                exclude = False
                pure_filename = os.path.basename(file_name)
                pure_directory = os.path.dirname(file_name)
                immediate_parent_folder = ""

                for exclude_dir in dirs_to_exclude:
                    # Directories to Exclude
                    if os.path.normpath(exclude_dir) in pure_directory.replace(soos.context.source_code_path, ""):
                        # skip this manifest
                        soos.console_log_verbose("Skipping file due to dirs_to_exclude: " + file_name)
                        exclude = True
                        continue

                if pure_directory.startswith("./"):
                    pure_directory = code_root + pure_directory[2:]
                elif pure_directory == ".":
                    pure_directory = code_root

                # Files to Exclude
                full_file_path = pure_directory
                if full_file_path.find("/") >= 0:
                    if not full_file_path.endswith("/"):
                        full_file_path += "/" + pure_filename
                else:
                    if not full_file_path.endswith("\\"):
                        full_file_path += "\\" + pure_filename

                for exclude_file in files_to_exclude:
                    # Files to Exclude
                    if fnmatch.fnmatch(pure_filename, exclude_file) or exclude_file in pure_filename:
                        # skip this manifest

                        soos.console_log_verbose("Skipping file due to files_to_exclude: " + file_name)

                        exclude = True
                        continue

                if not exclude:
                    # log the manifest

                    SOOS.console_log("Found manifest file: " + file_name)

                    # append manifest file content to manifests array

                    try:
                        try:
                            # attempt to get immediate parent folder
                            if full_file_path.find("/") >= 0:
                                # get furthest-right folder (immediate parent)
                                immediate_parent_folder = pure_directory.split("/")[-1]
                            else:
                                immediate_parent_folder = pure_directory.split("\\")[-1]

                        except Exception as e:

                            SOOS.console_log("Exception attempting to get immediate parent folder :: " + str(e) + "::" +
                                             "Result: Setting immediate parent folder to <blank string>"
                                             )
                            pass

                        manifest_label = immediate_parent_folder

                        with open(file_name, mode='r', encoding="utf-8") as the_file:
                            content = the_file.read()
                            if len(content.strip()) > 0:
                                manifestArr.append(SOOSManifestModel(pure_filename, manifest_label, content))
                    except Exception as e:
                        SOOS.console_log("Could not send manifest: " + file_name + " due to error: " + str(e))

        if len(manifestArr) == 0:
            SOOS.console_log(
                f"Sorry, we could not locate any manifests under {soos.context.source_code_path} Please check your files and try again.")
            return 0

        elif len(manifestArr) > MAX_MANIFESTS:
            SOOS.console_log(f"Maximum number of manifests exceeded. Taking first {MAX_MANIFESTS} only.")
            has_more_than_maximum_manifests = True
            manifestArr = manifestArr[0:MAX_MANIFESTS]

        try:
            add_manifests_response = SOOSManifestAPI.exec(
                soos_context=soos.context,
                project_id=project_id,
                analysis_id=analysis_id,
                manifests=manifestArr,
                has_more_than_maximum_manifests=has_more_than_maximum_manifests
            )

            if add_manifests_response is None or add_manifests_response.code is None:
                SOOS.console_log(
                    "There was some error with the Manifest API. For more information, please visit https://soos.io/support")
                return None
            else:
                SOOS.console_log(
                    f"Manifest upload status: {add_manifests_response.statusCode} || {add_manifests_response.code} || {add_manifests_response.message}")

                if type(add_manifests_response) is AddManifestsResponse:
                    if add_manifests_response.validManifestCount is not None:
                        SOOS.console_log(f"Valid manifest count: {add_manifests_response.validManifestCount}")
                    if add_manifests_response.invalidManifestCount is not None:
                        SOOS.console_log(f"Invalid manifest count: {add_manifests_response.invalidManifestCount}")
                    if add_manifests_response.manifests is not None:
                        for manifest in add_manifests_response.manifests:
                            soos.console_log_verbose(f"{manifest.name}: {manifest.statusMessage}")

            if (type(add_manifests_response) is AddManifestsResponse
                    and add_manifests_response.validManifestCount is not None):
                return add_manifests_response.validManifestCount
            else:
                return None

        except Exception as e:
            SOOS.console_log("Could not upload manifest files due to an error: " + str(e))
            return None

    @staticmethod
    def recursive_glob(treeroot, pattern):
        results = []
        for base, dirs, files in os.walk(treeroot):
            goodfiles = fnmatch.filter(files, pattern)
            results.extend(os.path.join(base, f) for f in goodfiles)
        return results

    @staticmethod
    def get_current_directory():
        current_folder = os.getcwd()
        plt = platform.system().lower()
        if plt != "windows":
            if current_folder[-1:] != "/":
                current_folder += "/"
        else:
            if current_folder[-1:] != "\\":
                current_folder += "\\"

        return current_folder

    @staticmethod
    def console_log(message):
        time_now = datetime.utcnow().isoformat(timespec="seconds", sep=" ")

        print(time_now + " SOOS: " + message)

    def console_log_verbose(self, message):
        if self.context.verbose_logging is True:
            SOOS.console_log(message)

    @staticmethod
    def print_vulnerabilities(vulnerabilities, violations):
        if vulnerabilities > 0 or violations > 0:
            SOOS.console_log(f"Vulnerabilities: {vulnerabilities}")
            SOOS.console_log(f"Violations: {violations}")

    def analysis_result_exec(self, report_status_url, analysis_result_max_wait, analysis_result_polling_interval):

        analysis_start_time = datetime.utcnow()

        while True:

            if (datetime.utcnow() - analysis_start_time).seconds > analysis_result_max_wait:
                SOOS.console_log(
                    f"Analysis Result Max Wait Time Reached ({str(analysis_result_max_wait)})"
                )
                sys.exit(1)

            analysis_result_api_response = SOOSAnalysisResultAPI.exec(self.context, report_status_url)

            content_object = analysis_result_api_response.json()

            if analysis_result_api_response.status_code < 299:

                analysis_status = str(content_object["status"]) if content_object and "status" in content_object \
                    else None
                vulnerabilities = content_object[
                    "vulnerabilities"] if content_object is not None and "vulnerabilities" in content_object and \
                                          content_object["vulnerabilities"] is not None else dict({"count": 0})
                violations = content_object[
                    "violations"] if content_object is not None and "violations" in content_object and content_object[
                    "violations"] is not None else dict({"count": 0})

                if analysis_status.lower() == "finished":
                    print()
                    SOOS.console_log("------------------------------------------------")
                    SOOS.console_log("Analysis Completed Successfully")
                    SOOS.console_log("------------------------------------------------")
                    SOOS.print_vulnerabilities(vulnerabilities=vulnerabilities['count'], violations=violations['count'])
                    return
                elif analysis_status.lower().startswith("failed"):
                    print()
                    SOOS.console_log("------------------------------------------------")
                    SOOS.console_log("Analysis complete - Failures reported.")
                    SOOS.console_log("------------------------------------------------")
                    SOOS.print_vulnerabilities(vulnerabilities=vulnerabilities['count'], violations=violations['count'])

                    # Fail with error
                    if self.script.on_failure == SOOSOnFailure.CONTINUE_ON_FAILURE:
                        return
                    else:
                        soos.console_log_verbose("Failures reported, failing build.")
                        sys.exit(1)

                elif analysis_status.lower() == "error":
                    SOOS.console_log(f"Analysis Error. Will retry in {str(analysis_result_polling_interval)} seconds.")
                    time.sleep(analysis_result_polling_interval)
                    continue
                else:
                    # Status code that is not pertinent to the result
                    SOOS.console_log(
                        "Analysis Ongoing. Will retry in " +
                        str(analysis_result_polling_interval) + " seconds."
                    )
                    time.sleep(analysis_result_polling_interval)
                    continue

            else:
                print()
                SOOS.console_log("------------------------------------------------")
                if "message" in analysis_result_api_response.json():
                    results_error_code = analysis_result_api_response.json()["code"]
                    results_error_message = analysis_result_api_response.json()["message"]
                    SOOS.console_log(
                        "Analysis Results API Status Code:" + str(results_error_code) + results_error_message)
                    SOOS.console_log("------------------------------------------------")
                    sys.exit(1)

    def upload_sarif_report(self, project_hash: str, branch_hash: str, scan_id: str):
        if self.context.generate_sarif_report is True:
            SOOSSARIFReport.exec(context=self.context, project_hash=project_hash, branch_hash=branch_hash,
                                 scan_id=scan_id)


class SOOSAnalysisStartAPI:
    API_RETRY_COUNT = 3

    URI_TEMPLATE = "{soos_base_uri}clients/{soos_client_id}/projects/{soos_project_id}/analysis/{soos_analysis_id}"

    def __init__(self):
        pass

    @staticmethod
    def generate_api_url(soos_context, project_id, analysis_id):
        return SOOSAnalysisStartAPI.URI_TEMPLATE.format(soos_base_uri=soos_context.base_uri,
                                                        soos_client_id=soos_context.client_id,
                                                        soos_project_id=project_id,
                                                        soos_analysis_id=analysis_id)

    @staticmethod
    def exec(soos_context, project_id, analysis_id):

        url = SOOSAnalysisStartAPI.generate_api_url(soos_context, project_id, analysis_id)

        analysis_start_response = None

        for i in range(0, SOOSAnalysisStartAPI.API_RETRY_COUNT):
            try:
                analysis_start_response = requests.put(
                    url=url,
                    data="{}",
                    headers={'x-soos-apikey': soos_context.api_key,
                             'content-length': str(0),
                             'Content-Type': 'multipart/form-data'}
                )

                break

            except Exception as e:
                SOOS.console_log("Analysis Start API Exception Occurred. "
                                 "Attempt " + str(i + 1) + " of " + str(SOOSAnalysisStartAPI.API_RETRY_COUNT))

        return analysis_start_response


class SOOSAnalysisResultAPI:
    API_RETRY_COUNT = 3

    def __init__(self):

        pass

    @staticmethod
    def exec(soos_context, result_uri):

        analysis_result_response = None

        for i in range(0, SOOSAnalysisResultAPI.API_RETRY_COUNT):
            try:
                analysis_result_response = requests.get(
                    url=result_uri,
                    headers={'x-soos-apikey': soos_context.api_key, 'Content-Type': 'application/json'}
                )

                break

            except Exception as e:
                SOOS.console_log(
                    "Analysis Result API Exception Occurred. "
                    "Attempt " + str(i + 1) + " of " + str(SOOSAnalysisResultAPI.API_RETRY_COUNT)
                )

        return analysis_result_response

class SOOSPatchStatusAPI:
    API_RETRY_COUNT = 3

    URI_TEMPLATE = "{soos_base_uri}clients/{soos_client_id}/projects/{project_hash}/branches/{branch_hash}/scan-types/{scan_type}/scans/{scan_id}"

    def __init__(self):
        pass

    @staticmethod
    def generate_api_url(soos_context, create_scan_api_response):
        url = SOOSPatchStatusAPI.URI_TEMPLATE
        url = url.replace("{soos_base_uri}", soos_context.base_uri)
        url = url.replace("{soos_client_id}", soos_context.client_id)
        url = url.replace("{project_hash}", create_scan_api_response.projectHash)
        url = url.replace("{branch_hash}", create_scan_api_response.branchHash)
        url = url.replace("{scan_type}", SCAN_TYPE)
        url = url.replace("{scan_id}", create_scan_api_response.analysisId)
        return url

    @staticmethod
    def exec(soos_context, create_scan_api_response, status, message):

        api_url = SOOSPatchStatusAPI.generate_api_url(soos_context, create_scan_api_response)

        patch_status_data = {
            "Status": status,
            "Message": message
        }

        for i in range(0, SOOSPatchStatusAPI.API_RETRY_COUNT):
            try:
                response = requests.patch(
                    url=api_url,
                    data=json.dumps(patch_status_data),
                    headers={'x-soos-apikey': soos_context.api_key, 'Content-Type': 'application/json'})

                json_response = handle_response(api_response=response)

                if type(json_response) is ErrorAPIResponse:
                    raise Exception(f"{json_response.code}-{json_response.message}")

                break

            except Exception as e:
                SOOS.console_log("Error updating scan status. "
                                 "Attempt " + str(i + 1) + " of " + str(SOOSPatchStatusAPI.API_RETRY_COUNT) + "::" +
                                 "Exception: " + str(e)
                                 )

class SOOSSARIFReport:
    API_RETRY_COUNT = 3

    URL_TEMPLATE = '{soos_base_uri}clients/{clientHash}/projects/{projectHash}/branches/{branchHash}/scan-types/sca/scans/{scanId}/formats/sarif'
    GITHUB_URL_TEMPLATE = 'https://api.github.com/repos/{project_name}/code-scanning/sarifs'

    errors_dict = {
        400: "Github: The sarif report is invalid",
        403: "Github: The repository is archived or if github advanced security is not enabled for this repository",
        404: "Github: Resource not found",
        413: "Github: The sarif report is too large",
        503: "Github: Service Unavailable"
    }

    def __init__(self):
        pass

    @staticmethod
    def generate_soos_sarif_url(base_uri: str, client_id: str, project_hash: str, branch_hash: str,
                                scan_id: str) -> str:
        return SOOSSARIFReport.URL_TEMPLATE.format(soos_base_uri=base_uri,
                                                   clientHash=client_id,
                                                   projectHash=project_hash,
                                                   branchHash=branch_hash,
                                                   scanId=scan_id)

    @staticmethod
    def generate_github_sarif_url(project_name: str) -> str:
        return SOOSSARIFReport.GITHUB_URL_TEMPLATE.format(project_name=project_name)

    @staticmethod
    def exec(context: SOOSContext, project_hash: str, branch_hash: str, scan_id: str):
        try:
            SOOS.console_log("Uploading SARIF Response")
            url = SOOSSARIFReport.generate_soos_sarif_url(base_uri=context.base_uri,
                                                          client_id=context.client_id,
                                                          project_hash=project_hash,
                                                          branch_hash=branch_hash,
                                                          scan_id=scan_id)

            headers = generate_header(api_key=context.api_key, content_type="application/json")
            attempt = 0
            sarif_json_response = None

            for attempt in range(0, SOOSSARIFReport.API_RETRY_COUNT):
                api_response: requests.Response = requests.get(url=url, headers=headers)
                sarif_json_response = handle_response(api_response)
                if type(sarif_json_response) is ErrorAPIResponse:
                    error_message = f"A Generate SARIF Report API Exception Occurred. Attempt {str(attempt + 1)} of {str(SOOSSARIFReport.API_RETRY_COUNT)}"
                    SOOS.console_log(f"{error_message}\n{sarif_json_response.code}-{sarif_json_response.message}")
                else:
                    SOOS.console_log("SARIF Report")
                    SOOS.console_log(str(sarif_json_response))
                    break

            raise_max_retry_exception(attempt=attempt, retry_count=SOOSSARIFReport.API_RETRY_COUNT)

            if sarif_json_response is None:
                SOOS.console_log("This project contains no issues. There will be no SARIF upload.")
                return
            else:
                SOOS.console_log("Uploading SARIF Report to GitHub")
                sarif_report_str = json.dumps(sarif_json_response)
                compressed_sarif_response = base64.b64encode(gzip.compress(bytes(sarif_report_str, 'UTF-8')))

                github_body_request = {
                    "commit_sha": context.commit_hash,
                    "ref": context.branch_name,
                    "sarif": compressed_sarif_response.decode(encoding='UTF-8'),
                    "started_at": ANALYSIS_START_TIME,
                    "tool_name": "SOOS SCA"
                }

                github_sarif_url = SOOSSARIFReport.generate_github_sarif_url(project_name=context.project_name)
                headers = {"Accept": "application/vnd.github.v3+json", "Authorization": f"token {context.github_pat}"}

                sarif_github_response = requests.post(url=github_sarif_url, data=json.dumps(github_body_request),
                                                      headers=headers)

                if sarif_github_response.status_code >= 400:
                    SOOSSARIFReport.handle_github_sarif_error(status=sarif_github_response.status_code,
                                                              json_response=sarif_github_response.json())
                else:
                    sarif_id = sarif_github_response.json()["id"]
                    sarif_url = sarif_github_response.json()["url"]
                    github_sarif_report_status = requests.get(url=sarif_url, headers=headers)

                    if github_sarif_report_status.ok:
                        processing_status = github_sarif_report_status.json()[
                            "processing_status"] if "processing_status" in github_sarif_report_status.json() else None
                        errors = github_sarif_report_status.json()[
                            "errors"] if "errors" in github_sarif_report_status.json() else None
                        SOOS.console_log(f"Upload SARIF Report to Github Status: {processing_status}")
                        if errors is not None and len(errors) > 0:
                            SOOS.console_log(f"Errors: {str(errors)}")

        except Exception as sarif_exception:
            SOOS.console_log(f"ERROR: {str(sarif_exception)}")

    @staticmethod
    def handle_github_sarif_error(status, json_response):

        error_message = json_response["message"] if json_response is not None and json_response[
            "message"] is not None else SOOSSARIFReport.errors_dict[status]
        if error_message is None:
            error_message = "An unexpected error has occurred uploading the sarif report to GitHub"

        SOOS.console_log(f"ERROR: {error_message}")


class SOOSOnFailure:
    FAIL_THE_BUILD = "fail_the_build"
    CONTINUE_ON_FAILURE = "continue_on_failure"


class SOOSModeOfOperation:
    RUN_AND_WAIT = "run_and_wait"
    ASYNC_INIT = "async_init"
    ASYNC_RESULT = "async_result"


class SOOSAnalysisScript:
    MIN_ANALYSIS_RESULT_POLLING_INTERVAL = 10
    ASYNC_RESULT_FILE_NAME = "soos_async.json"
    SOOS_WORKSPACE_FOLDER = "soos/workspace"

    def __init__(self):

        self.code_root = SOOS.get_current_directory()

        self.async_result_file = None

        self.mode = None
        self.on_failure = None

        self.directories_to_exclude = None
        self.files_to_exclude = None
        self.package_managers = None

        self.working_directory = None

        self.analysis_result_max_wait = None
        self.analysis_result_polling_interval = None

    def __set_working_dir_and_async_result_file__(self, working_directory):
        """
        This method receives the working_directory passed as script argument.
        It is used to set the working_directory and async_result_file properties from SOOSAnalysisScript class.
        """
        plt = platform.system().lower()
        if plt == 'windows':
            path_resolver = WindowsPath
            pure_path_resolver = PureWindowsPath
        else:
            path_resolver = Path
            pure_path_resolver = PurePath
        if working_directory is not None:
            working_dir_path = path_resolver(working_directory)
            if not working_dir_path.is_dir() or not working_dir_path.exists():
                SOOS.console_log('ERROR: The working directory does not exist or it is not a directory')
                sys.exit(1)

            if working_directory.startswith("~/") or \
                    working_directory.startswith("$HOME/") or \
                    working_directory.find("%userprofile%/"):
                self.working_directory = str(working_dir_path.expanduser().resolve())
            else:
                self.working_directory = str(working_dir_path.resolve())

            async_result_file_path = pure_path_resolver.joinpath(working_dir_path,
                                                                 SOOSAnalysisScript.SOOS_WORKSPACE_FOLDER,
                                                                 SOOSAnalysisScript.ASYNC_RESULT_FILE_NAME).resolve()
        else:
            # FAllBACK - COULD RESULT IN ERROR DEPENDING ON MODE DESIRED
            self.working_directory = ""
            async_result_file_path = pure_path_resolver.joinpath(path_resolver(self.code_root),
                                                                 SOOSAnalysisScript.ASYNC_RESULT_FILE_NAME).resolve()

        self.async_result_file = str(async_result_file_path)

    def load_script_arguments(self, script_args):

        if script_args.mode is not None:
            self.mode = str(script_args.mode)
        else:
            self.mode = "run_and_wait"

        SOOS.console_log("MODE: " + self.mode)

        if script_args.on_failure is not None:
            self.on_failure = str(script_args.on_failure)
        else:
            self.on_failure = "continue_on_failure"

        SOOS.console_log("ON_FAILURE: " + self.on_failure)

        self.directories_to_exclude = ["node_modules", "soos"]

        if script_args.directories_to_exclude is not None and len(script_args.directories_to_exclude.strip()) > 0:
            SOOS.console_log(f"DIRS_TO_EXCLUDE: {script_args.directories_to_exclude.strip()}")
            temp_dirs_to_exclude: List[str] = script_args.directories_to_exclude.split(",")

            for directory in temp_dirs_to_exclude:
                self.directories_to_exclude.append(directory.strip())
        else:
            SOOS.console_log("DIRS_TO_EXCLUDE: <NONE>")

        self.files_to_exclude = []
        if script_args.files_to_exclude is not None and len(script_args.files_to_exclude.strip()) > 0:
            SOOS.console_log(f"FILES_TO_EXCLUDE: {script_args.files_to_exclude.strip()}")
            temp_files_to_exclude: List[str] = script_args.files_to_exclude.split(",")

            for a_file in temp_files_to_exclude:
                self.files_to_exclude.append(a_file.strip())
        else:
            SOOS.console_log("FILES_TO_EXCLUDE: <NONE>")

        self.package_managers = []
        if script_args.package_managers is not None and len(script_args.package_managers.strip()) > 0:
            SOOS.console_log(f"PACKAGE MANAGERS: {script_args.package_managers.strip()}")
            temp_package_managers: List[str] = script_args.package_managers.split(",")

            for package_managers in temp_package_managers:
                self.package_managers.append(package_managers.strip())
        else:
            SOOS.console_log("PACKAGE MANAGERS: <NONE>")    

        # WORKING DIRECTORY & ASYNC RESUlT FILE
        self.__set_working_dir_and_async_result_file__(script_args.working_directory)

        SOOS.console_log("WORKING_DIRECTORY: " + self.working_directory)
        SOOS.console_log("ASYNC_RESULT_FILE: " + self.async_result_file)

        # ANALYSIS RESULT MAX WAIT
        # Default: 300 (5 minutes)
        # Minimum: Any
        # Maximum: Unlimited
        self.analysis_result_max_wait = 5 * 60
        if script_args.analysis_result_max_wait is not None:
            self.analysis_result_max_wait = int(script_args.analysis_result_max_wait)

        SOOS.console_log("ANALYSIS_RESULT_MAX_WAIT: " + str(self.analysis_result_max_wait))

        # ANALYSIS RESULT POLLING INTERVAL
        # Default: 10 seconds
        # Minimum: 10 seconds
        # Maximum: Unlimited
        self.analysis_result_polling_interval = 10
        if script_args.analysis_result_polling_interval is not None:
            self.analysis_result_polling_interval = int(script_args.analysis_result_polling_interval)
            if self.analysis_result_polling_interval < SOOSAnalysisScript.MIN_ANALYSIS_RESULT_POLLING_INTERVAL:
                self.analysis_result_polling_interval = SOOSAnalysisScript.MIN_ANALYSIS_RESULT_POLLING_INTERVAL

        SOOS.console_log("ANALYSIS_RESULT_POLLING_INTERVAL: " + str(self.analysis_result_polling_interval))

    @staticmethod
    def register_arguments():

        parser = argparse.ArgumentParser(description="SOOS CI Integration Script")

        # SCRIPT PARAMETERS

        parser.add_argument("--mode", "-m", dest="mode",
                            help="Mode of operation: "
                                 "run_and_wait: Run Analysis & Wait ** Default Value, "
                                 "async_init: Async Init, "
                                 "async_result: Async Result",
                            type=str,
                            default="run_and_wait",
                            required=False
                            )

        parser.add_argument("--onFailure", "-of", dest="on_failure",
                            help="On Failure: "
                                 "fail_the_build: Fail The Build "
                                 "continue_on_failure: Continue On Failure ** Default Value",
                            type=str,
                            default="continue_on_failure",
                            required=False
                            )

        parser.add_argument("--directoriesToExclude", "-dte", dest="directories_to_exclude",
                            help="Listing of directories (relative to ./) to exclude from the search for manifest files.\n"
                                 "Example - Correct: bin/start/\n"
                                 "Example - Incorrect: ./bin/start/\n"
                                 "Example - Incorrect: /bin/start",
                            type=str,
                            required=False
                            )

        parser.add_argument("--filesToExclude", "-fte", dest="files_to_exclude",
                            help="Listing of files (relative to ./) to exclude from the search for manifest files.\n"
                                 "Example - Correct: bin/start/requirements.txt\n"
                                 "Example - Incorrect: ./bin/start/requirements.txt\n"
                                 "Example - Incorrect: /bin/start/requirements.txt",
                            type=str,
                            required=False
                            )

        parser.add_argument("--workingDirectory", "-wd", dest="working_directory",
                            help="Absolute path where SOOS may write and read persistent files for the given build.\n"
                                 "Example - Correct: /tmp/workspace/\n"
                                 "Example - Incorrect: ./bin/start/\n"
                                 "Example - Incorrect: tmp/workspace",
                            type=str,
                            required=False
                            )

        parser.add_argument("--resultMaxWait", "-armw", dest="analysis_result_max_wait",
                            help="Maximum seconds to wait for Analysis Result. Default 300.",
                            type=int,
                            default=300,
                            required=False
                            )

        parser.add_argument("--resultPollingInterval", "-arpi", dest="analysis_result_polling_interval",
                            help="Polling interval (in seconds) for analysis result completion (success/failure). "
                                 "Min value: 10",
                            type=int,
                            default=10,
                            required=False
                            )

        parser.add_argument("--packageManagers", "-pm", dest="package_managers",
                            help="A list of package managers, delimited by comma, to include when searching for manifest files.",
                            type=str,
                            required=False
                            )              

        # CONTEXT PARAMETERS

        parser.add_argument("--baseUri", "-buri", dest="base_uri",
                            help="API URI Path. Default Value: https://api.soos.io/api/",
                            type=str,
                            default="https://api.soos.io/api/",
                            required=False
                            )

        parser.add_argument("--sourceCodePath", "-scp", dest="source_code_path",
                            help="Root path to begin recursive search for manifests. Default Value: ./",
                            type=str,
                            required=False
                            )

        parser.add_argument("--projectName", "-pn", dest="project_name",
                            help="Project name for tracking results",
                            type=str,
                            required=False
                            )

        parser.add_argument("--clientId", "-cid", dest="client_id",
                            help="API Client ID",
                            type=str,
                            required=False
                            )

        parser.add_argument("--apiKey", "-akey", dest="api_key",
                            help="API Key",
                            type=str,
                            required=False
                            )

        parser.add_argument("--verbosity", "-v", dest="logging_verbosity",
                            help="Set logging verbosity level value (INFO/DEBUG)",
                            type=str,
                            default="INFO",
                            required=False
                            )

        parser.add_argument("--verbose", dest="logging_verbose",
                            help="Enable verbose logging",
                            action="store_true",
                            required=False
                            )

        # CI SPECIAL CONTEXT

        parser.add_argument("--commitHash", "-ch", dest="commit_hash",
                            help="Commit Hash Value",
                            type=str,
                            default=None,
                            required=False
                            )

        parser.add_argument("--branchName", "-bn", dest="branch_name",
                            help="Branch Name",
                            type=str,
                            default=None,
                            required=False
                            )

        parser.add_argument("--branchUri", "-bruri", dest="branch_uri",
                            help="Branch URI",
                            type=str,
                            default=None,
                            required=False
                            )

        parser.add_argument("--buildVersion", "-bldver", dest="build_version",
                            help="Build Version",
                            type=str,
                            default=None,
                            required=False
                            )

        parser.add_argument("--buildUri", "-blduri", dest="build_uri",
                            help="Build URI",
                            type=str,
                            default=None,
                            required=False
                            )

        parser.add_argument("--operatingEnvironment", "-oe", dest="operating_environment",
                            help="Operating Environment",
                            type=str,
                            default=None,
                            required=False
                            )

        parser.add_argument("--appVersion", "-appver", dest="app_version",
                            help="App Version. Intended for internal use only.",
                            type=str,
                            default=None,
                            required=False
                            )

        parser.add_argument("--integrationName", "-intn", dest="integration_name",
                            help="Integration Name (e.g. Provider)",
                            type=str,
                            default=None,
                            required=False
                            )

        parser.add_argument("--integrationType", "-intt", dest="integration_type",
                            help="Integration Type. Intended for internal use only.",
                            type=str,
                            default=None,
                            required=False
                            )

        parser.add_argument("-sarif", dest="generate_sarif_report",
                            help="Upload SARIF Report to GitHub",
                            type=bool,
                            default=False,
                            required=False
                            )

        parser.add_argument("-gpat", dest="github_pat",
                            help="GitHub Personal Authorization Token",
                            type=str,
                            default=False,
                            required=False
                            )                   

        return parser

# Initialize SOOS
soos = SOOS()

def entry_point():
    more_info = " For more information visit https://soos.io/status/"

    # Register and load script arguments
    parser = soos.script.register_arguments()
    args = parser.parse_args()

    soos.script.load_script_arguments(script_args=args)
    load_context_result = soos.context.load(script_args=args)

    if load_context_result is False:

        SOOS.console_log("Could not find required Environment/Script Variables. "
                         "One or more are missing or empty:")

        soos.context.print_invalid()

        if soos.script.on_failure == SOOSOnFailure.FAIL_THE_BUILD:
            sys.exit(1)
        else:
            sys.exit(0)

    # Ensure Working Directory is present if mode is ASYNC
    if soos.script.mode in (SOOSModeOfOperation.ASYNC_INIT, SOOSModeOfOperation.ASYNC_RESULT):
        if len(soos.script.working_directory) == 0:
            SOOS.console_log("Working Directory is required when mode is ASYNC. Exiting.")
            if soos.script.on_failure == SOOSOnFailure.FAIL_THE_BUILD:
                sys.exit(1)
            else:
                sys.exit(0)

    if soos.script.mode in (SOOSModeOfOperation.RUN_AND_WAIT, SOOSModeOfOperation.ASYNC_INIT):

        # Make API call and store response, assuming that status code < 299, ie successful call.
        create_scan_api_response = SOOSScanAPI.create_scan_metadata(context=soos.context)
        # structure_response = SOOSStructureAPI.exec(soos.context)

        if create_scan_api_response is None:
            SOOS.console_log("A Create Scan Metadata API error occurred: Could not execute API." + more_info)
            if soos.script.on_failure == SOOSOnFailure.FAIL_THE_BUILD:
                sys.exit(1)
            else:
                sys.exit(0)
        # a response is returned but with original_response status code
        elif type(create_scan_api_response) is ErrorAPIResponse:
            SOOS.console_log(
                f"SCAN METADATA API STATUS: {create_scan_api_response.code} =====> {create_scan_api_response.message} {more_info}")
            sys.exit(1)

        # ## SCAN METADATA API CALL SUCCESSFUL - CONTINUE

        print()
        SOOS.console_log("------------------------")
        SOOS.console_log("Scan Metadata Request Created")
        SOOS.console_log("------------------------")
        SOOS.console_log("Analysis Id: " + create_scan_api_response.analysisId)
        SOOS.console_log("Project Id:  " + create_scan_api_response.projectHash)
        SOOS.console_log("Scan Status URL: " + create_scan_api_response.scanStatusUrl)
        # Now get ready to send your manifests out for Start Analysis API

        valid_manifests_count = soos.send_manifests(
            project_id=create_scan_api_response.projectHash,
            analysis_id=create_scan_api_response.analysisId,
            dirs_to_exclude=soos.script.directories_to_exclude,
            files_to_exclude=soos.script.files_to_exclude,
            package_managers=soos.script.package_managers
        )

        if valid_manifests_count is not None and valid_manifests_count > 0:
            try:

                print()
                SOOS.console_log("------------------------")
                SOOS.console_log("Starting Analysis")
                SOOS.console_log("------------------------")

                response = SOOSAnalysisStartAPI.exec(
                    soos_context=soos.context,
                    project_id=create_scan_api_response.projectHash,
                    analysis_id=create_scan_api_response.analysisId
                )

                if response.status_code >= 400:
                    analysis_code = response.json()["code"]
                    analysis_message = response.json()["message"]
                    SOOS.console_log(f"ANALYSIS API STATUS: {analysis_code} =====> {analysis_message} {more_info}")
                    # 500 code means SOOS server had an unexpected error and probably didn't update scan status
                    if response.status_code >= 500:
                        SOOSPatchStatusAPI.exec(soos.context, create_scan_api_response, SCAN_STATUS_ERROR, "An unexpected error occurred while starting the scan.")
                    sys.exit(1)

                else:
                    print()
                    SOOS.console_log(
                        "Analysis request is running, once completed, access the report using the links below")
                    print()
                    SOOS.console_log("ReportUrl: " + create_scan_api_response.scanUrl)
                    print()

                if soos.script.mode == SOOSModeOfOperation.RUN_AND_WAIT:

                    soos.analysis_result_exec(
                        report_status_url=create_scan_api_response.scanStatusUrl,
                        analysis_result_max_wait=soos.script.analysis_result_max_wait,
                        analysis_result_polling_interval=soos.script.analysis_result_polling_interval
                    )

                    soos.upload_sarif_report(project_hash=create_scan_api_response.projectHash,
                                             branch_hash=create_scan_api_response.branchHash,
                                             scan_id=create_scan_api_response.analysisId)

                    sys.exit(0)

                elif soos.script.mode == SOOSModeOfOperation.ASYNC_INIT:

                    # Write file here for RESULT process to pick up when it runs later
                    file_contents = {"report_status_url": create_scan_api_response.scanStatusUrl}
                    file = open(soos.script.async_result_file, "w")
                    file.write(json.dumps(file_contents))
                    file.close()

                    SOOS.console_log("Write Analysis URL To File: " + soos.script.async_result_file)

                    sys.exit(0)

            except Exception as general_exception:
                SOOS.console_log("ERROR: " + str(general_exception))

                if soos.script.on_failure == SOOSOnFailure.FAIL_THE_BUILD:
                    sys.exit(1)
                else:
                    sys.exit(0)
        else:  # valid_manifests_count is None (error) or 0
            if valid_manifests_count is None:
                scan_status = SCAN_STATUS_ERROR
                scan_message = "An error occurred uploading manifests, cannot continue. For more help, please visit https://soos.io/support"
                SOOS.console_log(scan_message)
            else:
                scan_status = SCAN_STATUS_INCOMPLETE
                scan_message = "No valid manifests found, cannot continue. For more help, please visit https://soos.io/support"
                SOOS.console_log(scan_message)
            SOOSPatchStatusAPI.exec(soos.context, create_scan_api_response, scan_status, scan_message)
            if soos.script.on_failure == SOOSOnFailure.FAIL_THE_BUILD:
                sys.exit(1)
            else:
                sys.exit(0)

    elif soos.script.mode == SOOSModeOfOperation.ASYNC_RESULT:

        # Sit and wait for ASYNC RESULT

        try:
            with open(soos.script.async_result_file, mode='r', encoding="utf-8") as the_file:
                async_result_content = the_file.read()
                async_result_values = json.loads(async_result_content)
                soos.console_log("Getting Analysis Result For: " + async_result_values["report_status_url"])

                soos.analysis_result_exec(
                    async_result_values["report_status_url"],
                    soos.script.analysis_result_max_wait,
                    soos.script.analysis_result_polling_interval
                )

            sys.exit(0)

        except FileNotFoundError as file_not_found:
            SOOS.console_log("ERROR: The async file (containing the report URL) could not be found. Exiting.")
            if soos.script.on_failure == SOOSOnFailure.FAIL_THE_BUILD:
                sys.exit(1)
            else:
                sys.exit(0)
    else:

        SOOS.console_log("ERROR: Mode argument is not a valid SOOS Mode.")

        if soos.script.on_failure == SOOSOnFailure.FAIL_THE_BUILD:
            sys.exit(1)
        else:
            sys.exit(0)

if __name__ == "__main__":
    PyPI_URL = "https://pypi.org/project/soos-sca"
    SOOS.console_log(f"\n\nThis CLI has been packaged and uploaded to PyPI! You can find it here: {PyPI_URL} \n")
    SOOS.console_log("Checking latest version...")
    latest_version, github_url = GithubVersionChecker.get_latest_version()
    current_version = f"v{SCRIPT_VERSION}"

    if latest_version is not None and latest_version != current_version:
        SOOS.console_log(
            f"Your current version {current_version} is out of date! Please update to the latest version {latest_version} on GitHub ({github_url}) or use the package on PyPI ({PyPI_URL}).")
    else:
        SOOS.console_log(f"Your current version {current_version} is the latest version available.")

    entry_point()

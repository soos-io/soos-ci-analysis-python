import json
from datetime import datetime
import sys
import glob
import fnmatch
import os
import argparse
import time
import urllib.parse
import platform

from pathlib import Path  # User Home Folder references
import requests

class SOOSStructureAPIResponse:

    def __init__(self, structure_response):

        self.original_response = structure_response

        self.content_object = None

        self.structure_id = None
        self.project_id = None
        self.analysis_id = None
        self.report_url = None
        self.embed_url = None
        self.report_status_url = None

        if self.original_response is not None:

            self.content_object = json.loads(self.original_response.content)

            self.structure_id = self.content_object["Id"]
            self.project_id = self.content_object["projectId"]
            self.analysis_id = self.content_object["Id"]
            self.report_url = self.content_object["reportUrl"]
            self.embed_url = self.content_object["embedUrl"]
            self.report_status_url = self.content_object["reportStatusUrl"]


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
            "project": soos_context.project_name,
            "name": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
            "integrationType": soos_context.integration_type,
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
        
        for i in range(0, SOOSStructureAPI.API_RETRY_COUNT):
            try:
                kernel = requests.post(
                        url=api_url,
                        data=json.dumps(structure_api_data),
                        #files=structure_api_data,
                        headers={'x-soos-apikey': soos_context.api_key, 'Content-Type': 'application/json'})

                if kernel.status_code > 500:
                    # 
                    api_response = kernel
                
                elif kernel.status_code == 403:
                    api_reponse = kernel

                else:
                    api_response = SOOSStructureAPIResponse(kernel)


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

        # Special Context - loads from script arguments only
        self.commit_hash = None
        self.branch_name = None
        self.branch_uri = None
        self.build_version = None
        self.build_uri = None
        self.operating_environment = None
        self.integration_name = None

        # INTENTIONALLY HARDCODED
        self.integration_type = "CI"

    def reset(self):
        self.base_uri = None
        self.source_code_path = None
        self.project_name = None
        self.client_id = None
        self.api_key = None

    def load(self, args):

        # Prioritize context from environment variables
        # Any environment variables that are not set will
        # automatically be searched in the script arguments
        self.load_from_env_var()

        if not self.is_valid():

            # Attempt to get MISSING context from parameters
            self.load_from_parameters(args)

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
                self.source_code_path = os.environ['SOOS_ROOT_CODE_PATH']
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

    def load_from_parameters(self, args):
        '''
        The parameters that are present in load_from_env_var will have a chance to be overloaded here.
        All other parameters can only be found in the args list.

        :param args:
        :return:
        '''

        # Do not reset - enable parameters to override environment variables
        # self.reset()

        if args.base_uri is not None:
            self.base_uri = str(args.base_uri)
            SOOS.console_log("SOOS_API_BASE_URI Parameter Loaded: " + self.base_uri)

        if args.source_code_path is not None:
            self.source_code_path = str(args.source_code_path)
            SOOS.console_log("SOOS_ROOT_CODE_PATH Parameter Loaded: " + self.source_code_path)

        if args.project_name is not None:
            self.project_name = str(args.project_name)
            SOOS.console_log("SOOS_PROJECT_NAME Parameter Loaded: " + self.project_name)

        if args.client_id is not None:
            self.client_id = str(args.client_id)
            SOOS.console_log("SOOS_CLIENT_ID Parameter Loaded: SECRET")

        if args.api_key is not None:
            self.api_key = str(args.api_key)
            SOOS.console_log("SOOS_API_KEY Parameter Loaded: SECRET")

        # ##################################################
        # Special Context - loads from script arguments only
        # ##################################################

        if args.commit_hash is not None:
            if len(args.commit_hash) > 0:
                self.commit_hash = str(args.commit_hash)
                SOOS.console_log("SOOS_COMMIT_HASH Parameter Loaded: " + self.commit_hash)

        if args.branch_name is not None:
            if len(args.branch_name) > 0:
                self.branch_name = str(args.branch_name)
                SOOS.console_log("SOOS_BRANCH_NAME Parameter Loaded: " + self.branch_name)

        if args.branch_uri is not None:
            if len(args.branch_uri) > 0:
                self.branch_uri = str(args.branch_uri)
                SOOS.console_log("SOOS_BRANCH_URI Parameter Loaded: " + self.branch_uri)

        if args.build_version is not None:
            if len(args.build_version) > 0:
                self.build_version = str(args.build_version)
                SOOS.console_log("SOOS_BUILD_VERSION Parameter Loaded: " + self.build_version)

        if args.build_uri is not None:
            if len(args.build_uri) > 0:
                self.build_uri = str(args.build_uri)
                SOOS.console_log("SOOS_BUILD_URI Parameter Loaded: " + self.build_uri)

        # Operating environment, if missing, will default to sys.platform
        
        if args.operating_environment is not None:
            if len(args.operating_environment) > 0:
                self.operating_environment = str(args.operating_environment)
            else:
                self.operating_environment = sys.platform
        else:
            self.operating_environment = sys.platform
        SOOS.console_log("SOOS_OPERATING_ENVIRONMENT Parameter Loaded: " + self.operating_environment)

        if args.integration_name is not None:
            if len(args.integration_name) > 0:
                self.integration_name = str(args.integration_name)
                SOOS.console_log("SOOS_INTEGRATION_NAME Parameter Loaded: " + self.integration_name)

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
            SOOS.console_log("CLIENT_ID, if you do not already have one, will be provided with a subscription to SOOS.io services.")

        if self.api_key is None or len(self.api_key) == 0:
            SOOS.console_log("REQUIRED PARAMETER IS MISSING: SOOS_API_KEY")
            SOOS.console_log("API_KEY, if you do not already have one, will be provided with a subscription to SOOS.io services.")


class SOOSManifestAPI:

    API_RETRY_COUNT = 3

    URI_TEMPLATE = "{soos_base_uri}" \
                   "clients/{soos_client_id}" \
                   "/projects/{soos_project_id}" \
                   "/analysis/{soos_analysis_id}" \
                   "/manifests/{soos_manifest_label}/{soos_manifest_name}"

    def __init__(self):
        pass

    @staticmethod
    def generate_api_url(soos_context, project_id, analysis_id, manifest_label, manifest_name):

        manifest_label_for_url = urllib.parse.quote(manifest_label)
        manifest_name_for_url = urllib.parse.quote(manifest_name)

        api_url = SOOSManifestAPI.URI_TEMPLATE

        api_url = api_url.replace("{soos_base_uri}", soos_context.base_uri)
        api_url = api_url.replace("{soos_client_id}", soos_context.client_id)
        api_url = api_url.replace("{soos_project_id}", project_id)
        api_url = api_url.replace("{soos_analysis_id}", analysis_id)
        api_url = api_url.replace("{soos_manifest_name}", manifest_name_for_url)
        api_url = api_url.replace("{soos_manifest_label}", manifest_label_for_url)
        
        return api_url

    @staticmethod

    def exec(soos_context, project_id, analysis_id, manifest_label, manifest_name, manifest_content):

        manifest_name = manifest_name.replace(".", "*")
        manifest_label = manifest_label.replace(".", "").replace("/", "").replace("\\", "")

        api_url = SOOSManifestAPI.generate_api_url(
            soos_context, project_id, analysis_id, manifest_label, manifest_name
        )

        response = None

        for i in range(0, SOOSManifestAPI.API_RETRY_COUNT):
            try:
                SOOS.console_log("*** Putting manifest: " + manifest_name + " :: to: " + api_url)
               #manifest_content is class str, convert to dict 
                response = requests.put(
                    url=api_url,
                    files=dict(manifest=manifest_content),
                    headers={'x-soos-apikey': soos.context.api_key,
                            'Content_type': 'multipart/form-data'
                    }
                )

                SOOS.console_log("Manifest Put Executed: " + manifest_name)
                break

            except Exception as e:
                SOOS.console_log("Manifest API Exception Occurred. "
                      "Attempt " + str(i + 1) + " of " + str(SOOSManifestAPI.API_RETRY_COUNT))

        return response


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

    def find_manifest_files(self, pattern):
        return glob.glob(
            self.context.source_code_path + '/**/' + pattern,
            recursive=True
        )

    def send_manifests(self, project_id, analysis_id, dirs_to_exclude, files_to_exclude):

        manifests_found_count = 0

        code_root = SOOS.get_current_directory()

        SOOS.console_log("------------------------")
        SOOS.console_log("Begin Recursive Manifest Search")
        SOOS.console_log("------------------------")

        MANIFEST_FILES = self.load_manifest_types()

        
        for manifest_file in MANIFEST_FILES:
            files = []
            package_manager = manifest_file['packageManager']
            SOOS.console_log("Looking for " + package_manager + " files...")
             
            for entries in manifest_file["manifests"]:
                pattern = entries["pattern"]
                candidate_files = self.find_manifest_files(pattern = pattern) 

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
                    if exclude_dir in pure_directory:
                        # skip this manifest

                        SOOS.console_log("Skipping file due to dirs_to_exclude: " + file_name)
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
                    if exclude_file in pure_filename:
                        # skip this manifest

                        SOOS.console_log("Skipping file due to files_to_exclude: " + file_name)

                        exclude = True
                        continue

                if not exclude:
                    # log the manifest

                    SOOS.console_log("Found manifest file: " + file_name)

               
                    # call the api with the manifest file content as the body

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

                        with open(file_name, 'r') as the_file:

                            content = the_file.read()
                            #print("Here is the content", content)
                            if len(content.strip()) > 0:


                                response = SOOSManifestAPI.exec(
                                    soos_context=soos.context,
                                    project_id=project_id,
                                    analysis_id=analysis_id,
                                    manifest_label=manifest_label,
                                    manifest_name=pure_filename,
                                    manifest_content=content
                                )
                                
                                if "message" in response.json():
                        
                                    manifest_message = response.json()["message"]
                                    manifest_code = response.json()["code"]
                                    SOOS.console_log(f"MANIFEST API STATUS: {response.status_code} || {manifest_code} =====> {manifest_message}")
                                    print()
                                    manifests_found_count += 1 
                                else:
                                    SOOS.console_log("There was some error with the Manifest API. For more information, please visit https://soos.io/support")
                                    print()
                                    manifests_found_count += 1

                            else:

                                SOOS.console_log("WARNING: Manifest file is empty and will be ignored: " + file_name)

                    except Exception as e:
                        SOOS.console_log("Could not send manifest: " + file_name + " due to error: " + str(e))

                              

        return manifests_found_count

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
        time_now = datetime.utcnow().isoformat(timespec = "seconds", sep = " ")
        
        print(time_now + " SOOS: " + message)

    def analysis_result_exec(self, report_status_url, analysis_result_max_wait, analysis_result_polling_interval):

        analysis_start_time = datetime.utcnow()

        while True:

            if (datetime.utcnow() - analysis_start_time).seconds > analysis_result_max_wait:
                SOOS.console_log(
                    "Analysis Result Max Wait Time Reached (" + str(analysis_result_max_wait) + ")"
                )
                sys.exit(1)

            response = SOOSAnalysisResultAPI.exec(self.context, report_status_url)
            
            content_object = json.loads(response.content)

            if response.status_code < 299:

                analysis_status = str(content_object["status"])

                if analysis_status.lower() == "finished":
                    SOOS.console_log("------------------------")
                    SOOS.console_log("Analysis Completed Successfully")
                    SOOS.console_log("------------------------")
                    sys.exit(0)
                elif analysis_status.lower().startswith("failed"):
                    SOOS.console_log("------------------------")
                    SOOS.console_log("Analysis complete - Failures reported.")

                    # Additional Messaging based on type of failure...
                    if analysis_status.lower().find("violation") >= 0:
                        SOOS.console_log("FAILURE: Violations reported.")
                    elif analysis_status.lower().find("vulnerabilit") >= 0:
                        SOOS.console_log("FAILURE: Vulnerabilities reported.")
                    else:
                        # Unknown failure - no additional messaging-out
                        pass
                    SOOS.console_log("------------------------")

                    # Fail with error
                    sys.exit(1)

                elif analysis_status.lower() == "error":
                    SOOS.console_log(
                        "Analysis Error. Will retry in " +
                        str(analysis_result_polling_interval) + " seconds."
                    )
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
                SOOS.console_log("------------------------")
                if "message" in response.json():
                    results_error_code = response.json()["code"]
                    results_error_message = response.json()["message"]
                    SOOS.console_log("Analysis Results API Status Code:" + str(results_error_code) + results_error_message)
                    SOOS.console_log("------------------------")
                    sys.exit(1)


class SOOSAnalysisStartAPI:

    API_RETRY_COUNT = 3

    URI_TEMPLATE = "{soos_base_uri}clients/{soos_client_id}/projects/{soos_project_id}/analysis/{soos_analysis_id}"

    def __init__(self):
        pass

    @staticmethod
    def generate_api_url(soos_context, project_id, analysis_id):
        api_url = SOOSAnalysisStartAPI.URI_TEMPLATE
        api_url = api_url.replace("{soos_base_uri}", soos_context.base_uri)
        api_url = api_url.replace("{soos_client_id}", soos_context.client_id)
        api_url = api_url.replace("{soos_project_id}", project_id)
        api_url = api_url.replace("{soos_analysis_id}", analysis_id)

        return api_url

    @staticmethod
    def exec(soos_context, project_id, analysis_id):

        url = SOOSAnalysisStartAPI.generate_api_url(soos_context, project_id, analysis_id)

        response = None

        for i in range(0, SOOSAnalysisStartAPI.API_RETRY_COUNT):
            try:
                response = requests.put(
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

        return response


class SOOSAnalysisResultAPI:

    API_RETRY_COUNT = 3

    def __init__(self):

        pass

    @staticmethod
    def exec(soos_context, result_uri):

        response = None

        for i in range(0, SOOSAnalysisResultAPI.API_RETRY_COUNT):
            try:
                response = requests.get(
                    url=result_uri,
                    headers={'x-soos-apikey': soos_context.api_key, 'Content-Type': 'application/json'}
                )

                break

            except Exception as e:
                SOOS.console_log(
                    "Analysis Result API Exception Occurred. "
                      "Attempt " + str(i + 1) + " of " + str(SOOSAnalysisResultAPI.API_RETRY_COUNT)
                )

        return response


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

        self.working_directory = None

        self.analysis_result_max_wait = None
        self.analysis_result_polling_interval = None

    def load_script_arguments(self):

        if args.mode is not None:
            self.mode = str(args.mode)
        else:
            self.mode = "run_and_wait"

        SOOS.console_log("MODE: " + self.mode)

        if args.on_failure is not None:
            self.on_failure = str(args.on_failure)
        else:
            self.on_failure = "fail_the_build"

        SOOS.console_log("ON_FAILURE: " + self.on_failure)


        self.directories_to_exclude = ["node_modules"]

        temp_dirs_to_exclude = []
        if args.directories_to_exclude is not None and len(args.directories_to_exclude.strip()) > 0:
            SOOS.console_log("DIRS_TO_EXCLUDE: " + args.directories_to_exclude.strip())
            temp_dirs_to_exclude = args.directories_to_exclude.split(",")

            for dir in temp_dirs_to_exclude:
                self.directories_to_exclude.append(dir)
        else:
            SOOS.console_log("DIRS_TO_EXCLUDE: <NONE>")

        self.files_to_exclude = []
        temp_files_to_exclude = []
        if args.files_to_exclude is not None and len(args.files_to_exclude.strip()) > 0:
            SOOS.console_log("FILES_TO_EXCLUDE: " + args.files_to_exclude.strip())
            temp_files_to_exclude = args.files_to_exclude.split(",")

            for a_file in temp_files_to_exclude:
                self.files_to_exclude.append(a_file)
        else:
            SOOS.console_log("FILES_TO_EXCLUDE: <NONE>")

        # WORKING DIRECTORY & ASYNC RESUlT FILE
        if args.working_directory is not None:
            self.working_directory = args.working_directory.strip()
            if len(self.working_directory) > 0:

                # IS THIS LINUX OR WINDOWS?
                if self.working_directory.find("/") >= 0:

                    # Convert references to user home folder to absolute path
                    if self.working_directory.startswith("~/"):
                        home = str(Path.home())

                        if home.endswith("/"):
                            self.working_directory = home + self.working_directory[2:]
                        else:
                            self.working_directory = home + "/" + self.working_directory[2:]

                    if not self.working_directory.endswith("/"):
                        self.async_result_file = self.working_directory + "/" + SOOSAnalysisScript.SOOS_WORKSPACE_FOLDER + "/" + SOOSAnalysisScript.ASYNC_RESULT_FILE_NAME
                    else:
                        self.async_result_file = self.working_directory + SOOSAnalysisScript.SOOS_WORKSPACE_FOLDER + "/" + SOOSAnalysisScript.ASYNC_RESULT_FILE_NAME
                else:
                    if not self.working_directory.endswith("\\"):
                        self.async_result_file = self.working_directory + "\\" + SOOSAnalysisScript.ASYNC_RESULT_FILE_NAME

                    # Convert references to user home folder to absolute path
                    if self.working_directory.find("%userprofile%") >= 0:
                        home = str(Path.home())

                        if home.endswith("\\"):
                            self.working_directory = home + self.working_directory[2:]
                        else:
                            self.working_directory = home + "\\" + self.working_directory[2:]

                    if not self.working_directory.endswith("\\"):
                        self.async_result_file = self.working_directory + "\\" + SOOSAnalysisScript.SOOS_WORKSPACE_FOLDER + "\\" + SOOSAnalysisScript.ASYNC_RESULT_FILE_NAME
                    else:
                        self.async_result_file = self.working_directory + SOOSAnalysisScript.SOOS_WORKSPACE_FOLDER + "\\" + SOOSAnalysisScript.ASYNC_RESULT_FILE_NAME

        else:
            # FAllBACK - COULD RESULT IN ERROR DEPENDING ON MODE DESIRED
            self.working_directory = ""
            self.async_result_file = self.code_root + SOOSAnalysisScript.ASYNC_RESULT_FILE_NAME

        SOOS.console_log("WORKING_DIRECTORY: " + self.working_directory)
        SOOS.console_log("ASYNC_RESULT_FILE: " + self.async_result_file)

        # ANALYSIS RESULT MAX WAIT
        # Default: 300 (5 minutes)
        # Minimum: Any
        # Maximum: Unlimited
        analysis_result_max_wait = 5 * 60
        if args.analysis_result_max_wait is not None:
            self.analysis_result_max_wait = int(args.analysis_result_max_wait)

        SOOS.console_log("ANALYSIS_RESULT_MAX_WAIT: " + str(self.analysis_result_max_wait))

        # ANALYSIS RESULT POLLING INTERVAL
        # Default: 10 seconds
        # Minimum: 10 seconds
        # Maximum: Unlimited
        self.analysis_result_polling_interval = 10
        if args.analysis_result_polling_interval is not None:
            self.analysis_result_polling_interval = int(args.analysis_result_polling_interval)
            if self.analysis_result_polling_interval < SOOSAnalysisScript.MIN_ANALYSIS_RESULT_POLLING_INTERVAL:
                self.analysis_result_polling_interval = SOOSAnalysisScript.MIN_ANALYSIS_RESULT_POLLING_INTERVAL

        SOOS.console_log("ANALYSIS_RESULT_POLLING_INTERVAL: " + str(self.analysis_result_polling_interval))

    @staticmethod
    def register_arguments():

        parser = argparse.ArgumentParser(description="SOOS CI Integration Script")

        # SCRIPT PARAMETERS

        parser.add_argument("-m", dest="mode",
                            help="Mode of operation: "
                                 "run_and_wait: Run Analysis & Wait ** Default Value, "
                                 "async_init: Async Init, "
                                 "async_result: Async Result",
                            type=str,
                            default="run_and_wait",
                            required=False
                            )

        parser.add_argument("-of", dest="on_failure",
                            help="On Failure: "
                                 "fail_the_build: Fail The Build ** Default Value, "
                                 "continue_on_failure: Continue On Failure",
                            type=str,
                            default="fail_the_build",
                            required=False
                            )

        parser.add_argument("-dte", dest="directories_to_exclude",
                            help="Listing of directories (relative to ./) to exclude from the search for manifest files.\n"
                                 "Example - Correct: bin/start/\n"
                                 "Example - Incorrect: ./bin/start/\n"
                                 "Example - Incorrect: /bin/start",
                            type=str,
                            required=False
                            )

        parser.add_argument("-fte", dest="files_to_exclude",
                            help="Listing of files (relative to ./) to exclude from the search for manifest files.\n"
                                 "Example - Correct: bin/start/requirements.txt\n"
                                 "Example - Incorrect: ./bin/start/requirements.txt\n"
                                 "Example - Incorrect: /bin/start/requirements.txt",
                            type=str,
                            required=False
                            )

        parser.add_argument("-wd", dest="working_directory",
                            help="Absolute path where SOOS may write and read persistent files for the given build.\n"
                                 "Example - Correct: /tmp/workspace/\n"
                                 "Example - Incorrect: ./bin/start/\n"
                                 "Example - Incorrect: tmp/workspace",
                            type=str,
                            required=False
                            )

        parser.add_argument("-armw", dest="analysis_result_max_wait",
                            help="Maximum seconds to wait for Analysis Result. Default 300.",
                            type=int,
                            default=300,
                            required=False
                            )

        parser.add_argument("-arpi", dest="analysis_result_polling_interval",
                            help="Polling interval (in seconds) for analysis result completion (success/failure). "
                                 "Min value: 10",
                            type=int,
                            default=10,
                            required=False
                            )

        # CONTEXT PARAMETERS

        parser.add_argument("-buri", dest="base_uri",
                            help="API URI Path. Default Value: https://api.soos.io/api/",
                            type=str,
                            # default="https://api.soos.io/api/",
                            required=False
                            )

        parser.add_argument("-scp", dest="source_code_path",
                            help="Root path to begin recursive search for manifests. Default Value: ./",
                            type=str,
                            # default="./",
                            required=False
                            )

        parser.add_argument("-pn", dest="project_name",
                            help="Project name for tracking results",
                            type=str,
                            required=False
                            )

        parser.add_argument("-cid", dest="client_id",
                            help="API Client ID",
                            type=str,
                            required=False
                            )

        parser.add_argument("-akey", dest="api_key",
                            help="API Key",
                            type=str,
                            required=False
                            )

        # CI SPECIAL CONTEXT

        parser.add_argument("-ch", dest="commit_hash",
                            help="Commit Hash Value",
                            type=str,
                            default=None,
                            required=False
                            )

        parser.add_argument("-bn", dest="branch_name",
                            help="Branch Name",
                            type=str,
                            default=None,
                            required=False
                            )

        parser.add_argument("-bruri", dest="branch_uri",
                            help="Branch URI",
                            type=str,
                            default=None,
                            required=False
                            )

        parser.add_argument("-bldver", dest="build_version",
                            help="Build Version",
                            type=str,
                            default=None,
                            required=False
                            )

        parser.add_argument("-blduri", dest="build_uri",
                            help="Build URI",
                            type=str,
                            default=None,
                            required=False
                            )

        parser.add_argument("-oe", dest="operating_environment",
                            help="Operating Environment",
                            type=str,
                            default=None,
                            required=False
                            )

        parser.add_argument("-intn", dest="integration_name",
                            help="Integration Name (e.g. Provider)",
                            type=str,
                            default=None,
                            required=False
                            )

        return parser


if __name__ == "__main__":

    #if ((3, 0) <= sys.version_info <= (3, 9)):
    if sys.version_info < (3, 6):
        print("**** SOOS FATAL ERROR: Python Version 3.6 or higher is required ****")
        sys.exit(1)
    

  
    # Initialize SOOS
    soos = SOOS()
    more_info = " For more information visit https://soos.io/status/"

    # Register and load script arguments
    parser = soos.script.register_arguments()
    args = parser.parse_args()

    soos.script.load_script_arguments()
    soos.context.load(args)
    MANIFEST_TEMPLATE = "{soos_base_uri}clients/{soos_client_id}/manifests"


    if not soos.context.load(args):

        SOOS.console_log("Could not find required Environment/Script Variables. "
                          "One or more are missing or empty:")

        soos.context.print_invalid()

        if soos.script.on_failure == SOOSOnFailure.FAIL_THE_BUILD:
            sys.exit(1)
        else:
            sys.exit(0)

    # Ensure Working Directory is present if mode is ASYNC
    if soos.script.mode in(SOOSModeOfOperation.ASYNC_INIT, SOOSModeOfOperation.ASYNC_RESULT):
        if len(soos.script.working_directory) == 0:
            SOOS.console_log("Working Directory is required when mode is ASYNC. Exiting.")
            if soos.script.on_failure == SOOSOnFailure.FAIL_THE_BUILD:
                sys.exit(1)
            else:
                sys.exit(0)

    if soos.script.mode in (SOOSModeOfOperation.RUN_AND_WAIT, SOOSModeOfOperation.ASYNC_INIT):
        
        # Make API call and store response, assuming that status code < 299, ie successful call.
        structure_response = SOOSStructureAPI.exec(soos.context)
        
        if structure_response is None:
           
            SOOS.console_log("A Structure API error occurred: Could not execute API." + more_info)
            if soos.script.on_failure == SOOSOnFailure.FAIL_THE_BUILD:
                sys.exit(1)
            else:
                sys.exit(0)
        # a response is returned but with original_response status code 
        elif structure_response.original_response.status_code >= 299:
            if "message" in structure_response.original_response.json():
                structure_code = structure_response.original_response.json()["code"]
                structure_message = structure_response.original_response.json()["message"]
                SOOS.console_log(f"STRUCTURE API STATUS: {structure_code} =====> {structure_message} {more_info}")
                sys.exit(1)
            #fallback in case the if clause doesnt work but there really is a > 299 response that deserves message.
            else: 
                SOOS.console_log("A Structure API error occurred: Could not execute API." + more_info)
                sys.exit(1)
            


        # ## STRUCTURE API CALL SUCCESSFUL - CONTINUE
        
        SOOS.console_log("------------------------")
        SOOS.console_log("Analysis Structure Request Created")
        SOOS.console_log("------------------------")
        SOOS.console_log("Analysis Id: " + structure_response.analysis_id)
        SOOS.console_log("Project Id:  " + structure_response.project_id)
        #Now get ready to send your manifests out for Start Analysis API 

        manifests_found_count = soos.send_manifests(
            structure_response.project_id,
            structure_response.analysis_id,
            soos.script.directories_to_exclude,
            soos.script.files_to_exclude
        )

        if manifests_found_count > 0:
            SOOS.console_log("You have sent a total of {} manifests to be analyzed.".format(manifests_found_count))
            try:

                SOOS.console_log("------------------------")
                SOOS.console_log("Starting Analysis")
                SOOS.console_log("------------------------")
                
                response = SOOSAnalysisStartAPI.exec(
                    soos_context=soos.context,
                    project_id=structure_response.project_id,
                    analysis_id=structure_response.analysis_id
                )

                if response.status_code >= 400:
                    analysis_code = response.json()["code"]
                    analysis_message = response.json()["message"]
                    SOOS.console_log(f"ANALYSIS API STATUS: {analysis_code} =====> {analysis_message} {more_info}")
                    sys.exit(1)

                else:
                    print()
                    SOOS.console_log("Analysis request is running, once completed, access the report using the links below")
                    print()
                    SOOS.console_log("ReportUrl: " + structure_response.report_url)
                    print()



                if soos.script.mode == SOOSModeOfOperation.RUN_AND_WAIT:

                    soos.analysis_result_exec(
                        structure_response.report_status_url,
                        soos.script.analysis_result_max_wait,
                        soos.script.analysis_result_polling_interval
                    )

                elif soos.script.mode == SOOSModeOfOperation.ASYNC_INIT:

                    # Write file here for RESULT process to pick up when it runs later
                    file_contents = {"report_status_url": structure_response.report_status_url}
                    file = open(soos.script.async_result_file, "w")
                    file.write(json.dumps(file_contents))
                    file.close()

                    SOOS.console_log("Write Analysis URL To File: " + soos.script.async_result_file)

                    sys.exit(0)
         
            except Exception as e:
                SOOS.console_log(

                    "ERROR: " + str(e)
                )

                if soos.script.on_failure == SOOSOnFailure.FAIL_THE_BUILD:
                    sys.exit(1)
                else:
                    sys.exit(0)
        else:   #so the number of manifests is NOT > 0 OR there is an outage
            
            SOOS.console_log("Sorry, we could not locate any manifests under " + soos.context.source_code_path + "  Please check your files and try again.")
            SOOS.console_log("For more help, please visit https://soos.io/support")
            if soos.script.on_failure == SOOSOnFailure.FAIL_THE_BUILD:
                sys.exit(1)
            else:
                sys.exit(0)

    elif soos.script.mode == SOOSModeOfOperation.ASYNC_RESULT:

        # Sit and wait for ASYNC RESULT

        try:
            with open(soos.script.async_result_file, 'r') as the_file:
                async_result_content = the_file.read()
                async_result_values = json.loads(async_result_content)
                soos.console_log("Getting Analysis Result For: " + async_result_values["report_status_url"])
                 
                soos.analysis_result_exec(
                    async_result_values["report_status_url"],
                    soos.script.analysis_result_max_wait,
                    soos.script.analysis_result_polling_interval
                )

            sys.exit(0)

        except FileNotFoundError as e:
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

######
     

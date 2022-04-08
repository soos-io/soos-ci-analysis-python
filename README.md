# SOOS Security Analysis: Python Script

Scan your software for **vulnerabilities** and **license issues**.  Generate **SBOMs**. 

Use **SOOS Core SCA** to:

1. Find, fix and monitor known **vulnerabilities**
2. Review open source **license usage** within your project
3. Track tickets in **Jira** or **GitHub** Issues
4. Generate an **SBOM** 

## Supported Languages and Package Managers

* [Cargo - Rust](https://doc.rust-lang.org/cargo/)
* [Composer - PHP](https://maven.apache.org/)
* [Dart PM (Pub Package Manager) - Dart](https://pub.dev/)
* [Gradle - Java & Kotlin](https://gradle.org/)
* [Homebrew - (various languages)](https://brew.sh/)
* [Maven - Java](https://maven.apache.org/)
* [Mix - Elixir](https://hexdocs.pm/mix/Mix.html)
* [NuGet - .NET](https://www.nuget.org/)
* [NPM (Node Package Manager) - Node](https://www.npmjs.com/)
* [PyPI - Python](https://pypi.org/)
* [Rebar3 - Erlang](https://rebar3.readme.io/docs/getting-started)
* [Ruby Gems - Ruby](https://rubygems.org/)

Our full list of supported manifest formats can be found [here](https://kb.soos.io/help/soos-languages-supported).

## Need an Account?
**Visit [soos.io](https://app.soos.io/register) to create your trial account.**

## Setup

### QuickStart

#### Authorization
The script will always attempt to load a specific set of parameters from environment variables first; any environment variable values not found will be loaded from script arguments. It’s recommended to use environment variables for `SOOS_CLIENT_ID` and `SOOS_API_KEY` values while using script arguments for the remaining parameters. These values can be found in the SOOS App under Integrate.

#### Running the Script

1. Create a folder within the repo root called */soos/workspace*
2. Place *soos.py* and *requirements.txt* in the *soos* directory
3. Exclude the *soos* directory from being scanned by passing in the `dte` parameter
    1. Set `dte="soos"`
4. QuickStart Parameters
```bash
-m="run_and_wait" 
-of="fail_the_build" 
-dte="soos" 
-fte="" 
-wd="./" 
-armw=300
-arpi=10
-buri="https://api.soos.io/api/" 
-scp="./" 
-pn="PROJECT NAME GOES HERE"
```
- `pn` - (project name) REQUIRED. A custom project name that will present itself as a collection of test results within your soos.io dashboard. For SARIF Report, it should be `{repository_owner}/{repository_name}`   
- `m` - (mode) the mode of running the script. Use *run_and_wait* to run synchronously. Use *async_init* to start async scanning, add other tasks and then use *async_result* to wait for the scan to complete
- `of` - (on failure) the method for handling failed scans (when violations or vulnerabilities are encountered). Use *fail_the_build* to fail the build (return exit code 1) if a violation or vulnerability is encountered. Use *continue_on_fail* to ignore violations or vulnerabilities and let the build continue
- `dte` - (directories to exclude) the list of comma separated directories to exclude
- `fte` - (files to exclude) the list of comma separated manifest files to exclude from a scan
- `wd` - (working directory) the root of the repo codebase on the local file system. Every CI engine has its own way of providing this value through some sort of variable.
- `armw` - (analysis result max wait) the maximum time in milliseconds to wait for a scan to complete
- `arpi` - (analysis result polling interval) the time in milliseconds to wait between polling calls
- `scp` - (source code path) the root directory to start looking for manifests in (recursively)
- `cid` - (client id) your SOOS client identifier (not required if using the environment variable)
- `akey` - (api key) your SOOS API key (not required if using the environment variable)
- `sarif` - (generate sarif report) generate the SARIF Report for GitHub
- `gpat` - (GitHub Personal Access Token) A GitHub Personal Access Token used to upload the SARIF Report. It must have the `security_events` scope to use this endpoint for private repositories. It must have also the `public_repo` scope for public repositories only. 

### Full Shell Script Example
```bash
# run soos.py with the -h flag for help
# REQUIRED ARGS:
SOOS_PROJECT_NAME="YOUR_PROJECT_NAME_HERE"
SOOS_LATEST_REPO="https://api.github.com/repos/soos-io/soos-ci-analysis-python/releases/latest"
SOOS_TAGS="https://api.github.com/repos/soos-io/soos-ci-analysis-python/releases/tags/$tag"
# BUILD/BRANCH SPECIFIC ARGS:
SOOS_COMMIT_HASH=""                # ENTER COMMIT HASH HERE IF KNOWN
SOOS_BRANCH_NAME=""                # ENTER BRANCH NAME HERE IF KNOWN
SOOS_BRANCH_URI=""                 # ENTER BRANCH URI HERE IF KNOWN
SOOS_BUILD_VERSION=""              # ENTER BUILD VERSION HERE IF KNOWN
SOOS_BUILD_URI=""                  # ENTER BUILD URI HERE IF KNOWN
SOOS_OPERATING_ENVIRONMENT=""      # ENTER OPERATING ENVIRONMENT HERE IF KNOWN (default will be provided)
SOOS_INTEGRATION_NAME="Script"

# OPTIONAL ARGS:
WORKSPACE="C:/Users/user/folder1/repo1" #PUT YOUR REPO PATH HERE
SOOS_MODE="run_and_wait"
SOOS_ON_FAILURE="fail_the_build"
SOOS_DIRS_TO_EXCLUDE="soos"
SOOS_FILES_TO_EXCLUDE=""
SOOS_ANALYSIS_RESULT_MAX_WAIT=300
SOOS_ANALYSIS_RESULT_POLLING_INTERVAL=10
SOOS_CHECKOUT_DIR="./"
SOOS_API_BASE_URL="https://api.soos.io/api/"


# **************************** Modify Above Only ***************#
mkdir -p "${WORKSPACE}/soos/workspace"
cd "${WORKSPACE}/soos"

curl -s $SOOS_LATEST_REPO | grep "browser_download_url" | cut -d '"' -f 4 | xargs -n 1 curl -LO
sha256sum -c soos.sha256
sha256sum -c requirements.sha256

cd ${WORKSPACE}

python -m venv ./
source bin/activate

pip install -r soos/requirements.txt
python soos/soos.py -m="${SOOS_MODE}" -of="${SOOS_ON_FAILURE}" -dte="${SOOS_DIRS_TO_EXCLUDE}" -fte="${SOOS_FILES_TO_EXCLUDE}" -wd="${SOOS_CHECKOUT_DIR}" -armw=${SOOS_ANALYSIS_RESULT_MAX_WAIT} -arpi=${SOOS_ANALYSIS_RESULT_POLLING_INTERVAL} -buri="${SOOS_API_BASE_URL}" -scp="${SOOS_CHECKOUT_DIR}" -pn="${SOOS_PROJECT_NAME}" -ch="${SOOS_COMMIT_HASH}" -bn="${SOOS_BRANCH_NAME}" -bruri="${SOOS_BRANCH_URI}" -bldver="${SOOS_BUILD_VERSION}" -blduri="${SOOS_BUILD_URI}" -oe="${SOOS_OPERATING_ENVIRONMENT}" -intn="${SOOS_INTEGRATION_NAME}"
```

### Full Windows CMD Script Example
```bat
echo off
:: run soos.py with the -h flag for help
:: ARGS REQUIRING CUSTOMIZATION:
:: SOOS_CLIENT_ID and SOOS_API_KEY must be defined as Environment variables. You can get these values from SOOS Application
set "SOOS_PROJECT_NAME=<Project Name>" :: ENTER PROJECT NAME
set "SOOS_LATEST_REPO=https://github.com/soos-io/soos-ci-analysis-python/releases/latest/download"

:: ARGS WHERE CUSTOMIZATION IS OPTIONAL:
set "SOURCE_CODE_PATH=<Source Code Main Directory>":: ENTER SOURCE CODE MAIN DIRECTORY
set "SOOS_MODE=run_and_wait"
set "SOOS_ON_FAILURE=fail_the_build"
set "SOOS_DIRS_TO_EXCLUDE=soos"
set "SOOS_FILES_TO_EXCLUDE="
set "SOOS_ANALYSIS_RESULT_MAX_WAIT=300"
set "SOOS_ANALYSIS_RESULT_POLLING_INTERVAL=10"
set "SOOS_CHECKOUT_DIR=./"

:: ARGS WHERE CUSTOMIZATION IS OPTIONAL, BUT UNLIKELY:
set "SOOS_API_BASE_URL=https://api.soos.io/api/"

:: CI ENGINE SPECIFIC:
set "SOOS_COMMIT_HASH="                :: ENTER BUILD VERSION HERE IF KNOWN
set "SOOS_BRANCH_NAME="                :: ENTER BRANCH NAME HERE IF KNOWN
set "SOOS_BRANCH_URI="                 :: ENTER BRANCH URI HERE IF KNOWN
set "SOOS_BUILD_VERSION="              :: ENTER BUILD VERSION HERE IF KNOWN
set "SOOS_BUILD_URI="                  :: ENTER BUILD URI HERE IF KNOWN
set "SOOS_OPERATING_ENVIRONMENT="      :: ENTER OPERATING ENVIRONMENT HERE IF KNOWN (default will be provided)
set "SOOS_INTEGRATION_NAME=Script"
set "SOOS_CLIENT_ID="
set "SOOS_API_KEY="

:: **************************** Modify Above Only *************** ::

set "ROOT=%SOURCE_CODE_PATH%/soos"
set "WORKSPACE=%ROOT%/workspace"
mkdir "%WORKSPACE%"

curl -LJO "%SOOS_LATEST_REPO%/soos.py" -o "%ROOT%/soos.py"
curl -LJO "%SOOS_LATEST_REPO%/requirements.txt" -o "%ROOT%/requirements.txt"

cd "%ROOT%"

python -m venv .
cd Scripts
call activate.bat

cd "%SOURCE_CODE_PATH%"

pip3 install -r "%ROOT%/requirements.txt"

python "%ROOT%/soos.py" -m="%SOOS_MODE%" -of="%SOOS_ON_FAILURE%" -dte="%SOOS_DIRS_TO_EXCLUDE%" -fte="%SOOS_FILES_TO_EXCLUDE%" -wd="%SOOS_CHECKOUT_DIR%" -armw=%SOOS_ANALYSIS_RESULT_MAX_WAIT% -arpi=%SOOS_ANALYSIS_RESULT_POLLING_INTERVAL% -buri="%SOOS_API_BASE_URL%" -scp="%SOOS_CHECKOUT_DIR%" -pn="%SOOS_PROJECT_NAME%" -ch="%SOOS_COMMIT_HASH%" -bn="%SOOS_BRANCH_NAME%" -bruri="%SOOS_BRANCH_URI%" -bldver="%SOOS_BUILD_VERSION%" -blduri="%SOOS_BUILD_URI%" -oe="%SOOS_OPERATING_ENVIRONMENT%" -intn="%SOOS_INTEGRATION_NAME%"
```

### Running the Script Asynchronously
You can run the script asynchronously by creating two script steps in your CI/CD pipeline/steps. The first will start the scan and the second will wait for the scan to complete.
The second step is optional if you don't care about the result in your CI/CD system.

#### Start the Scan
Use the script example above, setting the `SOOS_MODE` parameter to *async_init*. If you don't care about the scan result in your CI/CD pipeline, this is all you have to do!

#### Wait for the Scan
If you care about the result or want to break the build when issues occur, add a second step close to the end of your build pipeline/steps to give the scan as much time as possible to complete. Use the script example above, setting the `SOOS_MODE` parameter to *async_result*.

## Feedback and Support
### Knowledge Base
[Go To Knowledge Base](https://kb.soos.io/help)

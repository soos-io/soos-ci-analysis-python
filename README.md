# SOOS Security Analysis: Python Script
## OSS Security for Everyone
The SOOS Python Script is the most flexible way to run SOOS against your codebase to gain insights into your open source package risk. Run locally or on a CI/CD
server, using either synchronous or asynchronous mode.

## Supported Languages and Package Managers

*	Node (NPM)
*	Python (pypi)
*	.NET (NuGet)
*	Ruby (Ruby Gems)
*	Java (Maven)

Our full list of supported manifest formats can be found here: https://kb.soos.io/help/soos-languages-supported

## Need an Account?
**Visit [soos.io](https://app.soos.io/register) to create your free or trial account.**

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
```
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

### Full Shell Script Example
```
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
cd Scripts
source activate
cd ${WORKSPACE}


pip install -r soos/requirements.txt
python soos/soos.py -m="${SOOS_MODE}" -of="${SOOS_ON_FAILURE}" -dte="${SOOS_DIRS_TO_EXCLUDE}" -fte="${SOOS_FILES_TO_EXCLUDE}" -wd="${SOOS_CHECKOUT_DIR}" -armw=${SOOS_ANALYSIS_RESULT_MAX_WAIT} -arpi=${SOOS_ANALYSIS_RESULT_POLLING_INTERVAL} -buri="${SOOS_API_BASE_URL}" -scp="${SOOS_CHECKOUT_DIR}" -pn="${SOOS_PROJECT_NAME}" -ch="${SOOS_COMMIT_HASH}" -bn="${SOOS_BRANCH_NAME}" -bruri="${SOOS_BRANCH_URI}" -bldver="${SOOS_BUILD_VERSION}" -blduri="${SOOS_BUILD_URI}" -oe="${SOOS_OPERATING_ENVIRONMENT}" -intn="${SOOS_INTEGRATION_NAME}"
```

### Full Windows CMD Script Example
```
echo off
:: run soos.py with the -h flag for help
:: ARGS REQUIRING CUSTOMIZATION:
set "SOOS_PROJECT_NAME=YOUR_PROJECT_NAME_HERE"

:: ARGS WHERE CUSTOMIZATION IS OPTIONAL:
set "SOOS_MODE=run_and_wait"
set "SOOS_ON_FAILURE=fail_the_build"
set "SOOS_DIRS_TO_EXCLUDE=soos"
set "SOOS_FILES_TO_EXCLUDE="
set "SOOS_ANALYSIS_RESULT_MAX_WAIT=300"
set "SOOS_ANALYSIS_RESULT_POLLING_INTERVAL=10"
set "SOOS_CHECKOUT_DIR=../"

:: ARGS WHERE CUSTOMIZATION IS OPTIONAL, BUT UNLIKELY:
set "SOOS_API_BASE_URL=https://dev-api.soos.io/api/"
```
:: CI ENGINE SPECIFIC:
set "SOOS_COMMIT_HASH="                :: ENTER BUILD VERSION HERE IF KNOWN
set "SOOS_BRANCH_NAME="                :: ENTER BRANCH NAME HERE IF KNOWN
set "SOOS_BRANCH_URI="                 :: ENTER BRANCH URI HERE IF KNOWN
set "SOOS_BUILD_VERSION="              :: ENTER BUILD VERSION HERE IF KNOWN
set "SOOS_BUILD_URI="                  :: ENTER BUILD URI HERE IF KNOWN
set "SOOS_OPERATING_ENVIRONMENT="      :: ENTER OPERATING ENVIRONMENT HERE IF KNOWN (default will be provided)
set "SOOS_INTEGRATION_NAME=Script"

:: **************************** Modify Above Only *************** ::

set "ROOT=%CD%/soos"
set "WORKSPACE=%ROOT%/workspace"
mkdir "%WORKSPACE%"

set "ROOT=%CD%/soos"
set "WORKSPACE=%ROOT%/workspace"

cd "%ROOT%"
python -m venv .

cd "%WORKSPACE"
pip3 install -r "%CD%/requirements.txt" 

python soos.py -m="%SOOS_MODE%" -of="%SOOS_ON_FAILURE%" -dte="%SOOS_DIRS_TO_EXCLUDE%" -fte="%SOOS_FILES_TO_EXCLUDE%" -wd="%SOOS_CHECKOUT_DIR%" -armw=%SOOS_ANALYSIS_RESULT_MAX_WAIT% -arpi=%SOOS_ANALYSIS_RESULT_POLLING_INTERVAL% -buri="%SOOS_API_BASE_URL%" -scp="%SOOS_CHECKOUT_DIR%" -pn="%SOOS_PROJECT_NAME%" -ch="%SOOS_COMMIT_HASH%" -bn="%SOOS_BRANCH_NAME%" -bruri="%SOOS_BRANCH_URI%" -bldver="%SOOS_BUILD_VERSION%" -blduri="%SOOS_BUILD_URI%" -oe="%SOOS_OPERATING_ENVIRONMENT%" -intn="%SOOS_INTEGRATION_NAME%"


```

### Running the Script Asynchronously
You can run the script asynchronously by creating two script steps in your CI/CD pipeline/steps. The first will start the scan and the second will wait for the scan to complete.
The second step is optional if you don't care about the result in your CI/CD system.

#### Start the Scan
Use the script example above, setting the SOOS_MODE parameter to *async_init*. If you don't care about the scan result in your CI/CD pipeline, this is all you have to do!

#### Wait for the Scan
If you care about the result or want to break the build when issues occur, cadd a second step close to the end of your build pipeline/steps to give the scan as much time as possible to complete. Use the script example above, setting the SOOS_MODE parameter to *async_result*.

## Feedback and Support
### Support and Defects
https://www.soos.io/support

### Feature Requests
https://www.soos.io/support

### Request an Integration or Package Manager
https://www.soos.io/support


# run soos.py with the -h flag for help
#GET YOUR SOOS_CLIENT_ID and SOOS_API_KEY from the SOOS app and store them as enviromental variables

# REQUIRED ARGS:
SOOS_PROJECT_NAME="YOUR PROJECT NAME HERE"

# BUILD/BRANCH SPECIFIC ARGS:
SOOS_COMMIT_HASH=""                # ENTER COMMIT HASH HERE IF KNOWN
SOOS_BRANCH_NAME=""                # ENTER BRANCH NAME HERE IF KNOWN
SOOS_BRANCH_URI=""                 # ENTER BRANCH URI HERE IF KNOWN
SOOS_BUILD_VERSION=""              # ENTER BUILD VERSION HERE IF KNOWN
SOOS_BUILD_URI=""                  # ENTER BUILD URI HERE IF KNOWN
SOOS_OPERATING_ENVIRONMENT=""      # ENTER OPERATING ENVIRONMENT HERE IF KNOWN (default will be provided)
SOOS_INTEGRATION_NAME="Script"

# OPTIONAL ARGS:
WORKSPACE="C:/Users/user/folder/repo" #PATH TO YOUR REPO
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

curl -s https://api.github.com/repos/soos-io/soos-ci-analysis-python/releases/latest | grep "browser_download_url" | cut -d '"' -f 4 | xargs -n 1 curl -LO
sha256sum -c soos.sha256
sha256sum -c requirements.sha256

cd ${WORKSPACE}

python -m venv ./

cd Scripts
source activate
cd ${WORKSPACE}

pip3 install -r soos/requirements.txt
python soos/soos.py -m="${SOOS_MODE}" -of="${SOOS_ON_FAILURE}" -dte="${SOOS_DIRS_TO_EXCLUDE}" -fte="${SOOS_FILES_TO_EXCLUDE}" -wd="${SOOS_CHECKOUT_DIR}" -armw=${SOOS_ANALYSIS_RESULT_MAX_WAIT} -arpi=${SOOS_ANALYSIS_RESULT_POLLING_INTERVAL} -buri="${SOOS_API_BASE_URL}" -scp="${SOOS_CHECKOUT_DIR}" -pn="${SOOS_PROJECT_NAME}" -ch="${SOOS_COMMIT_HASH}" -bn="${SOOS_BRANCH_NAME}" -bruri="${SOOS_BRANCH_URI}" -bldver="${SOOS_BUILD_VERSION}" -blduri="${SOOS_BUILD_URI}" -oe="${SOOS_OPERATING_ENVIRONMENT}" -intn="${SOOS_INTEGRATION_NAME}"

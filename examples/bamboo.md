# Run and Wait Pattern

```
# run soos.py with the -h flag for help
#ARGS REQUIRING CUSTOMIZATION:
SOOS_PROJECT_NAME="YOUR_PROJECT_NAME_HERE"

# ARGS WHERE CUSTOMIZATION IS OPTIONAL:
SOOS_MODE="run_and_wait"
SOOS_ON_FAILURE="fail_the_build"
SOOS_DIRS_TO_EXCLUDE="soos"
SOOS_FILES_TO_EXCLUDE=""
SOOS_ANALYSIS_RESULT_MAX_WAIT=300
SOOS_ANALYSIS_RESULT_POLLING_INTERVAL=10

# ARGS WHERE CUSTOMIZATION IS OPTIONAL, BUT UNLIKELY:
SOOS_API_BASE_URL="https://api.soos.io/api/"

# CI ENGINE SPECIFIC:
eval SOOS_CHECKOUT_DIR="${bamboo.build.working.directory}"
ls -al $SOOS_CHECKOUT_DIR
SOOS_COMMIT_HASH="" # ENTER BUILD VERSION HERE IF KNOWN
SOOS_BRANCH_NAME="${bamboo.planRepository.branchName}"
SOOS_BRANCH_URI="" # ENTER BRANCH URI HERE IF KNOWN
SOOS_BUILD_VERSION="${bamboo.planRepository.revision}"
SOOS_BUILD_URI="${bamboo.resultsUrl}"
SOOS_OPERATING_ENVIRONMENT="" # ENTER OPERATING ENVIRONMENT HERE IF KNOWN (default will be provided)
SOOS_INTEGRATION_NAME="Bamboo"

# **************************** Modify Above Only ***************#
mkdir -p "${SOOS_CHECKOUT_DIR}/soos/workspace"
cd "${SOOS_CHECKOUT_DIR}"
python3 -m venv .
source bin/activate
pip3 install -r "${SOOS_CHECKOUT_DIR}/soos/requirements.txt"
python3 soos/soos.py -m="${SOOS_MODE}" -of="${SOOS_ON_FAILURE}" -dte="${SOOS_DIRS_TO_EXCLUDE}" -fte="${SOOS_FILES_TO_EXCLUDE}" -wd="${SOOS_CHECKOUT_DIR}" -armw=${SOOS_ANALYSIS_RESULT_MAX_WAIT} -arpi=${SOOS_ANALYSIS_RESULT_POLLING_INTERVAL} -buri="${SOOS_API_BASE_URL}" -scp="${SOOS_CHECKOUT_DIR}" -pn="${SOOS_PROJECT_NAME}"
```

# Async Pattern
```
INIT Step:
#run soos.py with the -h flag for help

#ARGS REQUIRING CUSTOMIZATION:
SOOS_PROJECT_NAME="YOUR_PROJECT_NAME_HERE"

#ARGS WHERE CUSTOMIZATION IS OPTIONAL:
SOOS_MODE="async_init"
SOOS_ON_FAILURE="fail_the_build"
SOOS_DIRS_TO_EXCLUDE="soos"
SOOS_FILES_TO_EXCLUDE=""
SOOS_ANALYSIS_RESULT_MAX_WAIT=300
SOOS_ANALYSIS_RESULT_POLLING_INTERVAL=10

#ARGS WHERE CUSTOMIZATION IS OPTIONAL, BUT UNLIKELY:
SOOS_API_BASE_URL="https://api.soos.io/api/"

#CI ENGINE SPECIFIC:
eval SOOS_CHECKOUT_DIR="${bamboo.build.working.directory}"
ls -al $SOOS_CHECKOUT_DIR
SOOS_COMMIT_HASH="" # ENTER BUILD VERSION HERE IF KNOWN
SOOS_BRANCH_NAME="${bamboo.planRepository.branchName}"
SOOS_BRANCH_URI="" # ENTER BRANCH URI HERE IF KNOWN
SOOS_BUILD_VERSION="${bamboo.planRepository.revision}"
SOOS_BUILD_URI="${bamboo.resultsUrl}"
SOOS_OPERATING_ENVIRONMENT="" # ENTER OPERATING ENVIRONMENT HERE IF KNOWN (default will be provided)
SOOS_INTEGRATION_NAME="Bamboo"

#**************************** Modify Above Only ***************
mkdir -p "${SOOS_CHECKOUT_DIR}/soos/workspace"
cd "${SOOS_CHECKOUT_DIR}"
python3 -m venv .
source bin/activate
pip3 install -r "${SOOS_CHECKOUT_DIR}/soos/requirements.txt"
python3 soos/soos.py -m="${SOOS_MODE}" -of="${SOOS_ON_FAILURE}" -dte="${SOOS_DIRS_TO_EXCLUDE}" -fte="${SOOS_FILES_TO_EXCLUDE}" -wd="${SOOS_CHECKOUT_DIR}" -armw=${SOOS_ANALYSIS_RESULT_MAX_WAIT} -arpi=${SOOS_ANALYSIS_RESULT_POLLING_INTERVAL} -buri="${SOOS_API_BASE_URL}" -scp="${SOOS_CHECKOUT_DIR}" -pn="${SOOS_PROJECT_NAME}"

RESULT Step


# run soos.py with the -h flag for help

# ARGS REQUIRING CUSTOMIZATION:
SOOS_PROJECT_NAME="YOUR_PROJECT_NAME_HERE"

# ARGS WHERE CUSTOMIZATION IS OPTIONAL:
SOOS_MODE="async_result"
SOOS_ON_FAILURE="fail_the_build"
SOOS_DIRS_TO_EXCLUDE="soos"
SOOS_FILES_TO_EXCLUDE=""
SOOS_ANALYSIS_RESULT_MAX_WAIT=300
SOOS_ANALYSIS_RESULT_POLLING_INTERVAL=10

# ARGS WHERE CUSTOMIZATION IS OPTIONAL, BUT UNLIKELY:
SOOS_API_BASE_URL="https://api.soos.io/api/"

# CI ENGINE SPECIFIC:
eval SOOS_CHECKOUT_DIR="${bamboo.build.working.directory}"
ls -al $SOOS_CHECKOUT_DIR
SOOS_COMMIT_HASH="" # ENTER BUILD VERSION HERE IF KNOWN
SOOS_BRANCH_NAME="${bamboo.planRepository.branchName}"
SOOS_BRANCH_URI="" # ENTER BRANCH URI HERE IF KNOWN
SOOS_BUILD_VERSION="${bamboo.planRepository.revision}"
SOOS_BUILD_URI="${bamboo.resultsUrl}"
SOOS_OPERATING_ENVIRONMENT="" # ENTER OPERATING ENVIRONMENT HERE IF KNOWN (default will be provided)
SOOS_INTEGRATION_NAME="Bamboo"

# **************************** Modify Above Only ***************#
mkdir -p "${SOOS_CHECKOUT_DIR}/soos/workspace"
cd "${SOOS_CHECKOUT_DIR}"
python3 -m venv .
source bin/activate
pip3 install -r "${SOOS_CHECKOUT_DIR}/soos/requirements.txt"
python3 soos/soos.py -m="${SOOS_MODE}" -of="${SOOS_ON_FAILURE}" -dte="${SOOS_DIRS_TO_EXCLUDE}" -fte="${SOOS_FILES_TO_EXCLUDE}" -wd="${SOOS_CHECKOUT_DIR}" -armw=${SOOS_ANALYSIS_RESULT_MAX_WAIT} -arpi=${SOOS_ANALYSIS_RESULT_POLLING_INTERVAL} -buri="${SOOS_API_BASE_URL}" -scp="${SOOS_CHECKOUT_DIR}" -pn="${SOOS_PROJECT_NAME}"

# ... Non-SOOS Steps May Go Here …
```

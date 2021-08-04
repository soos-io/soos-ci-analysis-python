# Run and Wait Pattern
### In this configuration we define a workflow that initiates a PackageAware scan and waits to receive the scan result before releasing the build thread.
```
version: 2.1

orbs:
  python: circleci/python@0.2.1

jobs:
  build-and-test:
    executor: python/default
    steps:
      - checkout
      - python/load-cache
      - python/install-deps
      - python/save-cache

      #### OTHER NON-SOOS STEPS MAY GO HERE #####

      - run:
          command: |
            # ARGS:
            # run soos.py with the -h flag for help
            
            # ARGS REQUIRING CUSTOMIZATION:
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
            eval SOOS_CHECKOUT_DIR="$CIRCLE_WORKING_DIRECTOR
            SOOS_COMMIT_HASH="${CIRCLE_SHA1}"
            SOOS_BRANCH_NAME="${CIRCLE_BRANCH}"
            SOOS_BRANCH_URI=""                 # ENTER BRANCH URI HERE IF KNOWN
            SOOS_BUILD_VERSION=""              # ENTER BUILD VERSION HERE IF KNOWN
            SOOS_BUILD_URI="${CIRCLE_BUILD_URL}"
            SOOS_OPERATING_ENVIRONMENT=""      # ENTER OPERATING ENVIRONMENT HERE IF KNOWN (default will be provided)
            SOOS_INTEGRATION_NAME="CircleCI"

            
            # **************************** Modify Above Only ***************#
            mkdir -p "${SOOS_CHECKOUT_DIR}/soos/workspace"
            cd "${SOOS_CHECKOUT_DIR}"
            python3 -m venv .
            source bin/activate
            pip3 install -r "${SOOS_CHECKOUT_DIR}/soos/requirements.txt"
            python3 soos/soos.py -m="${SOOS_MODE}" -of="${SOOS_ON_FAILURE}" -dte="${SOOS_DIRS_TO_EXCLUDE}" -fte="${SOOS_FILES_TO_EXCLUDE}" -wd="${SOOS_CHECKOUT_DIR}" -armw=${SOOS_ANALYSIS_RESULT_MAX_WAIT} -arpi=${SOOS_ANALYSIS_RESULT_POLLING_INTERVAL} -buri="${SOOS_API_BASE_URL}" -scp="${SOOS_CHECKOUT_DIR}" -pn="${SOOS_PROJECT_NAME}"
          name: SOOS

      # OTHER NON-SOOS STEPS MAY GO HERE #####

workflows:
  main:
    jobs:
      - build-and-test
```

# Async Pattern
### In this configuration we define a workflow that initiates a PackageAware scan, permits other business logic to execute for an indeterminate amount of time, and then returns back to PackageAware to receive the results.
```
version: 2.1

orbs:
  python: circleci/python@0.2.1

jobs:
  build-and-test:
    executor: python/default
    steps:
      - checkout
      - python/load-cache
      - python/install-deps
      - python/save-cache

    #Non-SOOS Steps May Go Here …


      - run:
          command: |
            # ARGS:
            # run soos.py with the -h flag for help
            
            # ARGS REQUIRING CUSTOMIZATION:
            SOOS_PROJECT_NAME="YOUR_PROJECT_NAME_HERE"
            
            # ARGS WHERE CUSTOMIZATION IS OPTIONAL:
            SOOS_MODE="async_init"
            SOOS_ON_FAILURE="fail_the_build"
            SOOS_DIRS_TO_EXCLUDE="soos"
            SOOS_FILES_TO_EXCLUDE=""
            SOOS_ANALYSIS_RESULT_MAX_WAIT=300
            SOOS_ANALYSIS_RESULT_POLLING_INTERVAL=10
            
            # ARGS WHERE CUSTOMIZATION IS OPTIONAL, BUT UNLIKELY:
            SOOS_API_BASE_URL="https://api.soos.io/api/"
            
            # CI ENGINE SPECIFIC:
            eval SOOS_CHECKOUT_DIR="$CIRCLE_WORKING_DIRECTOR
            SOOS_COMMIT_HASH="${CIRCLE_SHA1}"
            SOOS_BRANCH_NAME="${CIRCLE_BRANCH}"
            SOOS_BRANCH_URI=""                 # ENTER BRANCH URI HERE IF KNOWN
            SOOS_BUILD_VERSION=""              # ENTER BUILD VERSION HERE IF KNOWN
            SOOS_BUILD_URI="${CIRCLE_BUILD_URL}"
            SOOS_OPERATING_ENVIRONMENT=""      # ENTER OPERATING ENVIRONMENT HERE IF KNOWN (default will be provided)
            SOOS_INTEGRATION_NAME="CircleCI"
            
            # **************************** Modify Above Only ***************#
            mkdir -p "${SOOS_CHECKOUT_DIR}/soos/workspace"
            cd "${SOOS_CHECKOUT_DIR}"
            python3 -m venv .
            source bin/activate
            pip3 install -r "${SOOS_CHECKOUT_DIR}/soos/requirements.txt"
            python3 soos/soos.py -m="${SOOS_MODE}" -of="${SOOS_ON_FAILURE}" -dte="${SOOS_DIRS_TO_EXCLUDE}" -fte="${SOOS_FILES_TO_EXCLUDE}" -wd="${SOOS_CHECKOUT_DIR}" -armw=${SOOS_ANALYSIS_RESULT_MAX_WAIT} -arpi=${SOOS_ANALYSIS_RESULT_POLLING_INTERVAL} -buri="${SOOS_API_BASE_URL}" -scp="${SOOS_CHECKOUT_DIR}" -pn="${SOOS_PROJECT_NAME}"
          name: SOOS Async Init

    #Non-SOOS Steps May Go Here ...


      - run:
          command: |
            # ARGS:
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
            eval SOOS_CHECKOUT_DIR="$CIRCLE_WORKING_DIRECTOR
            SOOS_COMMIT_HASH="${CIRCLE_SHA1}"
            SOOS_BRANCH_NAME="${CIRCLE_BRANCH}"
            SOOS_BRANCH_URI=""                 # ENTER BRANCH URI HERE IF KNOWN
            SOOS_BUILD_VERSION=""              # ENTER BUILD VERSION HERE IF KNOWN
            SOOS_BUILD_URI="${CIRCLE_BUILD_URL}"
            SOOS_OPERATING_ENVIRONMENT=""      # ENTER OPERATING ENVIRONMENT HERE IF KNOWN (default will be provided)
            SOOS_INTEGRATION_NAME="CircleCI"
            
            # **************************** Modify Above Only ***************#
            mkdir -p "${SOOS_CHECKOUT_DIR}/soos/workspace"
            cd "${SOOS_CHECKOUT_DIR}"
            python3 -m venv .
            source bin/activate
            pip3 install -r "${SOOS_CHECKOUT_DIR}/soos/requirements.txt"
            python3 soos/soos.py -m="${SOOS_MODE}" -of="${SOOS_ON_FAILURE}" -dte="${SOOS_DIRS_TO_EXCLUDE}" -fte="${SOOS_FILES_TO_EXCLUDE}" -wd="${SOOS_CHECKOUT_DIR}" -armw=${SOOS_ANALYSIS_RESULT_MAX_WAIT} -arpi=${SOOS_ANALYSIS_RESULT_POLLING_INTERVAL} -buri="${SOOS_API_BASE_URL}" -scp="${SOOS_CHECKOUT_DIR}" -pn="${SOOS_PROJECT_NAME}"
          name: SOOS Async Result


    #Non-SOOS Steps May Go Here ...
  

workflows:
  main:
    jobs:
      - build-and-test
```

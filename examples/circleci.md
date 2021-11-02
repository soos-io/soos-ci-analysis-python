# Run and Wait Pattern
### In this configuration we define a workflow that initiates a PackageAware scan and waits to receive the scan result before releasing the build thread.
```yaml
version: 2.1

jobs:
  build-and-test:
    working_directory: ~/integration-test-circleci
    docker:
      # CircleCI Python images available at: https://hub.docker.com/r/circleci/python/
      - image: cimg/python:3.9.7
        environment: # environment variables for primary container
          SOOS_PROJECT_NAME: "YOUR_PROJECT_NAME_HERE"
          # ARGS WHERE CUSTOMIZATION IS OPTIONAL:
          SOOS_MODE: run_and_wait
          SOOS_ON_FAILURE: fail_the_build
          SOOS_DIRS_TO_EXCLUDE: soos
          SOOS_FILES_TO_EXCLUDE: ""
          SOOS_ANALYSIS_RESULT_MAX_WAIT: 300
          SOOS_ANALYSIS_RESULT_POLLING_INTERVAL: 10
          # ARGS WHERE CUSTOMIZATION IS OPTIONAL, BUT UNLIKELY:
          SOOS_API_BASE_URL: https://api.soos.io/api/
          # CI ENGINE SPECIFIC:
          SOOS_CHECKOUT_DIR: /home/circleci/integration-test-circleci
          SOOS_COMMIT_HASH: ${CIRCLE_SHA1}
          SOOS_BRANCH_NAME: ${CIRCLE_BRANCH}
          SOOS_BRANCH_URI: ""                 # ENTER BRANCH URI HERE IF KNOWN
          SOOS_BUILD_VERSION: ""              # ENTER BUILD VERSION HERE IF KNOWN
          SOOS_BUILD_URI: ${CIRCLE_BUILD_URL}
          SOOS_OPERATING_ENVIRONMENT: ""      # ENTER OPERATING ENVIRONMENT HERE IF KNOWN (default will be provided)
          SOOS_INTEGRATION_NAME: CircleCI
          SOOS_CLIENT_ID: Paste the SOOS Client Id
          SOOS_API_KEY: Paste the SOOS API Key
    steps:
      - checkout # check out source code to working directory
      - run:
          name: Create the soos dir
          command: mkdir -p soos
      - run: |
          cd soos
          curl -LJO https://github.com/soos-io/soos-ci-analysis-python/releases/latest/download/soos.py -o soos.py
          curl -LJO https://github.com/soos-io/soos-ci-analysis-python/releases/latest/download/requirements.txt -o requirements.txt
      - run:
          name: Install Python deps in a venv
          command: |
            pipenv install -r requirements.txt
            pip install requests
      - run:
          name: Run And Wait
          command: |
            python soos/soos.py -m="${SOOS_MODE}" -of="${SOOS_ON_FAILURE}" -dte="${SOOS_DIRS_TO_EXCLUDE}" -fte="${SOOS_FILES_TO_EXCLUDE}" -wd="${SOOS_CHECKOUT_DIR}" -armw=${SOOS_ANALYSIS_RESULT_MAX_WAIT} -arpi=${SOOS_ANALYSIS_RESULT_POLLING_INTERVAL} -buri="${SOOS_API_BASE_URL}" -scp="${SOOS_CHECKOUT_DIR}" -pn="${SOOS_PROJECT_NAME}"

workflows:
  main:
    jobs:
      - build-and-test
```

# Async Pattern
### In this configuration we define a workflow that initiates a PackageAware scan, permits other business logic to execute for an indeterminate amount of time, and then returns back to PackageAware to receive the results.

```yaml
version: 2.1

jobs:
  build-and-test:
    working_directory: ~/integration-test-circleci
    docker:
      # CircleCI Python images available at: https://hub.docker.com/r/circleci/python/
      - image: cimg/python:3.9.7
        environment: # environment variables for primary container
          SOOS_PROJECT_NAME: "YOUR_PROJECT_NAME_HERE"
          # ARGS WHERE CUSTOMIZATION IS OPTIONAL:
          SOOS_ON_FAILURE: fail_the_build
          SOOS_DIRS_TO_EXCLUDE: soos
          SOOS_FILES_TO_EXCLUDE: ""
          SOOS_ANALYSIS_RESULT_MAX_WAIT: 300
          SOOS_ANALYSIS_RESULT_POLLING_INTERVAL: 10
          # ARGS WHERE CUSTOMIZATION IS OPTIONAL, BUT UNLIKELY:
          SOOS_API_BASE_URL: https://api.soos.io/api/
          # CI ENGINE SPECIFIC:
          SOOS_CHECKOUT_DIR: /home/circleci/integration-test-circleci
          SOOS_COMMIT_HASH: ${CIRCLE_SHA1}
          SOOS_BRANCH_NAME: ${CIRCLE_BRANCH}
          SOOS_BRANCH_URI: ""                 # ENTER BRANCH URI HERE IF KNOWN
          SOOS_BUILD_VERSION: ""              # ENTER BUILD VERSION HERE IF KNOWN
          SOOS_BUILD_URI: ${CIRCLE_BUILD_URL}
          SOOS_OPERATING_ENVIRONMENT: ""      # ENTER OPERATING ENVIRONMENT HERE IF KNOWN (default will be provided)
          SOOS_INTEGRATION_NAME: CircleCI
          SOOS_CLIENT_ID: Paste the SOOS Client Id
          SOOS_API_KEY: Paste the SOOS API Key
    steps:
      - checkout # check out source code to working directory
      - run:
          command: mkdir -p soos
          name: Create the soos dir
      - run: |
          cd soos
          curl -LJO https://github.com/soos-io/soos-ci-analysis-python/releases/latest/download/soos.py -o soos.py
          curl -LJO https://github.com/soos-io/soos-ci-analysis-python/releases/latest/download/requirements.txt -o requirements.txt
      - run:
          command: |
            pipenv install -r requirements.txt
            pip install requests
          name: Install Python deps in a venv
      - run:
          name: 'SOOS Async Init'
          command: |
            python soos/soos.py -m="async_init" -of="${SOOS_ON_FAILURE}" -dte="${SOOS_DIRS_TO_EXCLUDE}" -fte="${SOOS_FILES_TO_EXCLUDE}" -wd="${SOOS_CHECKOUT_DIR}" -armw=${SOOS_ANALYSIS_RESULT_MAX_WAIT} -arpi=${SOOS_ANALYSIS_RESULT_POLLING_INTERVAL} -buri="${SOOS_API_BASE_URL}" -scp="${SOOS_CHECKOUT_DIR}" -pn="${SOOS_PROJECT_NAME}"
      - run:
          name: 'SOOS Async Result'
          command: |
            python soos/soos.py -m="async_result" -of="${SOOS_ON_FAILURE}" -dte="${SOOS_DIRS_TO_EXCLUDE}" -fte="${SOOS_FILES_TO_EXCLUDE}" -wd="${SOOS_CHECKOUT_DIR}" -armw=${SOOS_ANALYSIS_RESULT_MAX_WAIT} -arpi=${SOOS_ANALYSIS_RESULT_POLLING_INTERVAL} -buri="${SOOS_API_BASE_URL}" -scp="${SOOS_CHECKOUT_DIR}" -pn="${SOOS_PROJECT_NAME}"

workflows:
  main:
    jobs:
      - build-and-test
```

# SOOS Security Analysis: Python Script

Scan your software for **vulnerabilities** and **license issues**.  Generate **SBOMs**. 

Use **SOOS Core SCA** to:

1. Find, fix and monitor known **vulnerabilities**
2. Review open source **license usage** within your project
3. Track tickets in **Jira** or **GitHub** Issues
4. Generate an **SBOM** 

## Supported Languages and Package Managers

Our full list of supported manifest formats can be found [here](https://kb.soos.io/help/soos-languages-supported).

## Need an Account?
**Visit [soos.io](https://app.soos.io/register) to create your trial account.**

## Running the Script
See [Script Knowlege Base Documentation](https://github.com/soos-io/kb-docs/blob/main/SCA/Script.md)

### Linux Shell Script Example
See [Linux GitHub Gist](https://gist.githubusercontent.com/soostech/bf4fe3c320f7457a81f2e48ebe057aa5/raw/7fcba97f88c524b2d1e3eddf2c29de52af13a0c4/soos_sca.sh)

### Windows CMD Script Example
See [Windows Batch File Gist](https://gist.githubusercontent.com/soostech/37134fb636da3246d275b2ee220669c1/raw/0ab31b1c50869d8e8061deee4fa04e8ff7169f77/soos_sca.bat)

### Script Arguments
| Argument | Description |
| --- | --- |
| -h, --help | show this help message and exit |
| -hf, --helpFormatted | Print the --help command in markdown table format |
| -m, --mode | Mode of operation:<br>run_and_wait: Run Analysis & Wait ** Default Value,<br>async_init: Async Init,<br>async_result: Async Result |
| -of, --onFailure | On Failure:<br>fail_the_build: Fail The Build<br>continue_on_failure: Continue On Failure ** Default Value |
| -dte, --directoriesToExclude | Listing of directories (relative to ./) to exclude from the search for manifest files.<br>Example - Correct: bin/start/<br>Example - Incorrect: ./bin/start/<br>Example - Incorrect: /bin/start |
| -fte, --filesToExclude | Listing of files (relative to ./) to exclude from the search for manifest files.<br>Example - Correct: bin/start/requirements.txt<br>Example - Incorrect: ./bin/start/requirements.txt<br>Example - Incorrect: /bin/start/requirements.txt |
| -wd, --workingDirectory | Absolute path where SOOS may write and read persistent files for the given build.<br>Example - Correct: /tmp/workspace/<br>Example - Incorrect: ./bin/start/<br>Example - Incorrect: tmp/workspace |
| -armw, --resultMaxWait | Maximum seconds to wait for Analysis Result. Default 300. |
| -arpi, --resultPollingInterval | Polling interval (in seconds) for analysis result completion (success/failure).<br>Min value: 10 |
| -pm, --packageManagers | A list of package managers, delimited by comma, to include when searching for manifest files. |
| -buri, --baseUri | API URI Path. Default Value: https://api.soos.io/api/ |
| -scp, --sourceCodePath | Root path to begin recursive search for manifests. Default Value: ./ |
| -pn, --projectName | Project name for tracking results |
| -cid, --clientId | API Client ID |
| -akey, --apiKey | API Key |
| -v, --verbosity | Set logging verbosity level value (INFO/DEBUG) |
| --verbose | Enable verbose logging |
| -ch, --commitHash | Commit Hash Value |
| -bn, --branchName | Branch Name |
| -bruri, --branchUri | Branch URI |
| -bldver, --buildVersion | Build Version |
| -blduri, --buildUri | Build URI |
| -oe, --operatingEnvironment | Operating Environment |
| -appver, --appVersion | App Version. Intended for internal use only. |
| -intn, --integrationName | Integration Name (e.g. Provider) |
| -intt, --integrationType | Integration Type. Intended for internal use only. |
| -sarif | Upload SARIF Report to GitHub |
| -gpat | GitHub Personal Authorization Token |


## Feedback and Support

See [SOOS Knowledge Base](https://kb.soos.io/help)

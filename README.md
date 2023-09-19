# [SOOS Core SCA](https://soos.io/sca-product)

SOOS is an independent software security company, located in Winooski, VT USA, building security software for your team. [SOOS, Software security, simplified](https://soos.io).

Use SOOS to scan your software for [vulnerabilities](https://app.soos.io/research/vulnerabilities) and [open source license](https://app.soos.io/research/licenses) issues with [SOOS Core SCA](https://soos.io/sca-product). [Generate SBOMs](https://kb.soos.io/help/soos-reports-for-export). Govern your open source dependencies. Run the [SOOS DAST vulnerability scanner](https://soos.io/dast-product) against your web apps or APIs.

[Demo SOOS](https://app.soos.io/demo) or [Register for a Free Trial](https://app.soos.io/register).

If you maintain an Open Source project, sign up for the Free as in Beer [SOOS Community Edition](https://soos.io/products/community-edition).

## soos-ci-analysis-python
Python script to run SOOS Core SCA

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
| Argument | Default | Description |
| --- | --- | --- |
| -h, --help | ==SUPPRESS== | show this help message and exit |
| -hf, --helpFormatted | False | Print the --help command in markdown table format |
| -m, --mode | run_and_wait | Mode of operation:<br>run_and_wait: Run Analysis & Wait ** Default Value,<br>async_init: Async Init,<br>async_result: Async Result<br>For more information about scan modes, visit https://github.com/soos-io/kb-docs/blob/main/SCA/Script.md |
| -of, --onFailure | continue_on_failure | On Failure:<br>fail_the_build: Fail The Build<br>continue_on_failure: Continue On Failure ** Default Value |
| -dte, --directoriesToExclude | None | Listing of directories (relative to ./) to exclude from the search for manifest files.<br>Example - Correct: bin/start/<br>Example - Incorrect: ./bin/start/<br>Example - Incorrect: /bin/start |
| -fte, --filesToExclude | None | Listing of files (relative to ./) to exclude from the search for manifest files.<br>Example - Correct: bin/start/requirements.txt<br>Example - Incorrect: ./bin/start/requirements.txt<br>Example - Incorrect: /bin/start/requirements.txt |
| -wd, --workingDirectory | None | Absolute path where SOOS may write and read persistent files for the given build.<br>Example - Correct: /tmp/workspace/<br>Example - Incorrect: ./bin/start/<br>Example - Incorrect: tmp/workspace |
| -armw, --resultMaxWait | 300 | Maximum seconds to wait for Analysis Result. Default 300. |
| -arpi, --resultPollingInterval | 10 | Polling interval (in seconds) for analysis result completion (success/failure).<br>Min value: 10 |
| -pm, --packageManagers | None | A list of package managers, delimited by comma, to include when searching for manifest files. |
| -buri, --baseUri | https://api.soos.io/api/ | SOOS API URI Path. Default Value: https://api.soos.io/api/<br>Intended for internal use only. |
| -scp, --sourceCodePath | None | Root path to begin recursive search for manifests. Default Value: ./ |
| -pn, --projectName | None | Project name for tracking results, (this will be the one used inside of the SOOS App) |
| -cid, --clientId | None | Client ID, get yours from https://app.soos.io/integrate/sca |
| -akey, --apiKey | None | API Key, get yours from https://app.soos.io/integrate/sca |
| -v, --verbosity | INFO | Set logging verbosity level value (INFO/DEBUG) |
| --verbose | False | Enable verbose logging |
| -ch, --commitHash | None | Commit Hash Value |
| -bn, --branchName | None | Branch Name |
| -bruri, --branchUri | None | Branch URI |
| -bldver, --buildVersion | None | Build Version |
| -blduri, --buildUri | None | Build URI |
| -oe, --operatingEnvironment | None | Operating Environment |
| -appver, --appVersion | None | App Version. Intended for internal use only. |
| -intn, --integrationName | None | Integration Name (e.g. Provider) |
| -intt, --integrationType | None | Integration Type. Intended for internal use only. |
| -sarif | False | Generates SARIF Report that later can be uploaded to GitHub |


## Feedback and Support
See [SOOS Knowledge Base](https://kb.soos.io/help)


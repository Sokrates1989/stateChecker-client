# stateChecker-client
Sends a post request to the stateChecker server to verify, that the tool is working. Also checks, if the server is up and running and sends a telegram message, if not.

Use https://github.com/Sokrates1989/docker-stateChecker as server

## Requirements

Requires python, pyTelegramBotApi and git to be used in the base project.

## Install and information

This tool is meant to be used from within another python based project. 
Therefore you should add this tool as a submodule to your git project in the base git directory using 

```console
git submodule add https://github.com/Sokrates1989/stateChecker-client.git
```

See https://git-scm.com/book/en/v2/Git-Tools-Submodules

## Preparation for usage

### Edit config

If you only have to use one state check for your tool (common):
Rename config.txt.template to config.txt

If your tool consists of multiple parts that each require an individual state check:
Rename config.txt.multiple_checks_template to config.txt

```
root
├── yourCodeBase
│   ├── file_to_import_tool_from.py
│   └── ..
├── stateChecker-client
│   ├── config.txt
│   ├── config.txt.template
│   ├── config.txt.multiple_checks_template
│   └── ..
└── ..
```

Create a new token (just a random long string), that serves as your authentication.
Could use: https://onlinerandomtools.com/generate-random-string
!!! IMPORTANT: If you loose this, you cannot update, nor delete your state_checks any more !!!

### Add the install directory to your python imports 

```python
# Import submodules.
# Insert path to submodules to allow importing them.
import os
import sys
sys.path.insert(1, os.path.join(os.path.dirname(__file__), "path/",  "to/", "stateChecker-client"))
```

If your code structure is like below and you want to import this tool from file_to_import_tool_from.py, you may use the snippet below the folder structure example.

```
root
├── yourCodeBase
│   ├── file_to_import_tool_from.py
│   └── ..
├── stateChecker-client
└── ..
```

```python
# Import submodules.
# Insert path to submodules to allow importing them.
import os
import sys
sys.path.insert(1, os.path.join(os.path.dirname(__file__), "..", "stateChecker-client"))
```


### Import the tool 

```python
# Import stateChecker-client.
import stateCheckerClient as StateCheckerClient
```


## If you have a dev/live implementation

if you go live for the first time, you might have to remove submodule once and delete the submodule directory manually

```
git rm -r --cached stateChecker-client
```

remeber to also delete the directory stateChecker-client, then readd submodule as done in ##Install and information

```
git submodule add https://github.com/Sokrates1989/stateChecker-client.git
```



## Usage

### StateCheck

#### Continous checking
This will run on a seperate Thread will your tool is running and send frequent pings to to server to tell it, that the tool is working.

If you only have to use one state check for your tool (common):

```python
stateChecker = StateCheckerClient.StateCheckerClient()
stateChecker.start()
```

If your tool consists of multiple parts that each require an individual state check:
```python
stateChecker = StateCheckerClient.StateCheckerClient(0)
stateChecker.start()
```
```python
stateChecker = StateCheckerClient.StateCheckerClient(1)
stateChecker.start()
```

#### Single server call

This will call the statecheker server once. This is the usage of choice, if the base tool is being run on some kind of routine, e.g. cronjobs.

If you only have to use one state check for your tool (common):

```python
stateChecker = StateCheckerClient.StateCheckerClient()
stateChecker.indicate_tool_is_up_once()
```

If your tool consists of multiple parts that each require an individual state check:
```python
stateChecker = StateCheckerClient.StateCheckerClient(0)
stateChecker.indicate_tool_is_up_once()
```
```python
stateChecker = StateCheckerClient.StateCheckerClient(1)
stateChecker.indicate_tool_is_up_once()
```


### Backup

This will update the previous backup file hash and timestamp once.

If you only have to use one state check for your tool (common):

```python
stateChecker = StateCheckerClient.StateCheckerClient()
stateChecker.updateBackupFile(backupFileHash, backupFileCreationTimestamp)
```

If your tool consists of multiple parts that each require an individual state check:
```python
stateChecker = StateCheckerClient.StateCheckerClient(0)
stateChecker.updateBackupFile(backupFileHash, backupFileCreationTimestamp)
```
```python
stateChecker = StateCheckerClient.StateCheckerClient(1)
stateChecker.updateBackupFile(backupFileHash, backupFileCreationTimestamp)
```


### Multiple Tools Environment Var Usage

#### First or just one tool
```
"STATECHECKER_IS_BACKUP_FILE_CHECK"
"STATECHECKER_TOOL_NAME"
"STATECHECKER_TOOL_DESCRIPTION"
"STATECHECKER_TOOL_TOKEN"
"STATECHECKER_TOOL_FREQUENCY_IN_MINUTES"
```

#### Second tool
```
"STATECHECKER_IS_BACKUP_FILE_CHECK_1"
"STATECHECKER_TOOL_NAME_1"
"STATECHECKER_TOOL_DESCRIPTION_1"
"STATECHECKER_TOOL_TOKEN_1"
"STATECHECKER_TOOL_FREQUENCY_IN_MINUTES_1"
```

#### Third tool
```
"STATECHECKER_IS_BACKUP_FILE_CHECK_2"
"STATECHECKER_TOOL_NAME_2"
"STATECHECKER_TOOL_DESCRIPTION_2"
"STATECHECKER_TOOL_TOKEN_2"
"STATECHECKER_TOOL_FREQUENCY_IN_MINUTES_2"
```


#### More tools
...
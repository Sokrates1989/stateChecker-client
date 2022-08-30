# stateChecker-client
Sends a post request to the stateChecker server to verify, that the tool is working. Also checks, if the server is up and running and sends a telegram message, if not.

Use https://github.com/Sokrates1989/docker-stateChecker as server

## Requirements

Requires python in the base project.

## Install and information

This tool is meant to used from within another python based project. 
Therefore you should add add this tool as a submodule to your git project in the base git directory using 

```console
git submodule add https://github.com/Sokrates1989/stateChecker-client.git
```

See https://git-scm.com/book/en/v2/Git-Tools-Submodules

## Preparation for usage

### Edit config

Rename config.txt.template to config.txt

```
root
├── yourCodeBase
│   ├── file_to_import_tool_from.py
│   └── ..
├── stateChecker-client
│   ├── config.txt
│   ├── config.txt.template
│   └── ..
└── ..
```


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
import dockerStateCheckerClient as StateCheckerClient
```



## Usage

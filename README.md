

# ![NetStrikeLogo3](https://github.com/user-attachments/assets/00db6229-3905-4653-bfc0-c653079358ae)


NetStrike is a remote script manager based on a client-server architecture, where the server is responsible for executing scripts on demand from authenticated clients.

The project was initially developed for cybersecurity purposes, enabling the simulation of network attacks in a controlled environment.
Due to this focus, NetStrike has been built with a strong emphasis on security, featuring encryption, secure authentication (JWT), and input validation.

# Features
-Upload and manage scripts remotely

-Supported script types: .py, .sh, .ps1 (PowerShell support coming in future upgrades)

-Scheduled execution of scripts (future upgrade)

-Secure communication over HTTPS

-User authentication via JWT

-Input and output sanitization to prevent injection attacks

-Role-based access control (future upgrade)

# Example - Script Templates
Scripts must implement a specific interface depending on the language.

Python script
```Python
class Script(Interface_Script):
    def __init__(self):
        self.params = []
        self.keys = []

    def execute(self):
        # The actual script
        return "Output"

    def get_param(self):
        return self.keys

    def set_param(self, vet_param):
        self.params = vet_param
        return True
```
Bash script
```Bash
#!/bin/bash

param="Custom message"

set_param() {
    param="$1"
}

get_param() {
    echo "$param"
}

execute() {
    #The actual script
    echo "Output"
}

execute
```

# API Endpoints

## Authenticate user and receive JWT token

```https
  POST /login
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `username`      | `string` | **Required**. |
| `password`      | `string` | **Required**. |

##### Example of request
```yaml
POST /login
{
  "username": "yourUsername",
  "password": "yourPassword"
}
```

##### Example of response
```yaml
{
  "access_token": "yourToken"
}
```

## Get all scripts

```https
  GET /script_list
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `token` | `string` | **Required**. JWT token|

##### Example of request
```yaml
GET /script_list
Authorization: Bearer <token>
```

##### Example of response
```yaml
{
  "scripts": ["pythonScript.py", "usefulTool.sh"]
}
```

## Get script description

```https
  GET /script_details/<script_name>
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `script_name`      | `string` | **Required**. Name of the script (without extension) |
| `token` | `string` | **Required**. JWT token|

##### Example of request
```yaml
GET /script_details/pythonScript
Authorization: Bearer <token>
```

##### Example of response
```yaml
{
  "description": "This script returns the status of every port of the specified host.", 
  "params": "ip_address"
}
```

## Edit script

```https
  PATCH /edit_script/<script_name>
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `script_name`      | `string` | **Required**. Name of the script (without extension) |
| `token` | `string` | **Required**. JWT token|
| `name`      | `string` | **Required**. New name (set to None if it should not be changed) |
| `description`      | `string` | **Required**. New description (set to None if it should not be changed) |

##### Example of request
```yaml
PATCH /edit_script/pythonScript
Authorization: Bearer <token>

{
  "name": <name>,
  "description": <description>
}
```


##### Example of response
```yaml
{}
```

## Remove script

```https
  DELETE /remove_script/<script_name>
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `script_name`      | `string` | **Required**. Name of the script (without extension) |
| `token` | `string` | **Required**. JWT token|

##### Example of request
```yaml
DELETE /remove_script/pythonScript
Authorization: Bearer <token>
```

##### Example of response
```yaml
{}
```

## Execute script
All parameters are required unless otherwise stated.
The keys of the parameters in the body of the request must have the correct name (see 'get script description').
```https
  POST /execute/<script_name>
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `script_name`      | `string` | **Required**. Name of the script (without extension) |
| `token` | `string` | **Required**. JWT token|
| Request body      | `dictionary` | **Required**. Dictionary of parameters. The keys must match the expected names (see 'Get Script Description'). All parameters are required unless otherwise stated. |

##### Example of request
```yaml
POST /execute/pythonScript
Authorization: Bearer <token>

{
  "param1": "value",
  "param2": "value"
}
```

##### Example of response
```yaml
{
  "date": "2025-04-14 18:51:30",
  "result": "Output of pythonScript", 
  "status": "finished"
}
```

## Get all tests

```https
  GET /test_list
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `token` | `string` | **Required**. JWT token|

##### Example of request
```yaml
GET /test_list
Authorization: Bearer <token>
```

##### Example of response
```yaml
{
  "tests": ["2025-04-14 14:24:51", "2025-04-14 18:52:58", "Routine_test_3"]
}
```

## Get test description

```https
  GET /test_details/<test_name>
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `test_name`      | `string` | **Required**. Name of item to fetch |
| `token` | `string` | **Required**. JWT token|

##### Example of request
```yaml
GET /test_details/Routine_test_3
Authorization: Bearer <token>
```

##### Example of response
```yaml
{
  "name": "Routine_test_3",
  "date": "2025-04-14 18:51:30",
  "result": "Output of pythonScript", 
  "status": "finished",
  "script_executed": "pythonScript"
}
```

## Checks for updates of the plugin list or test list

```https
  GET /notification/<list>/<timestamp>
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `list`      | `string` | **Required**. Type of resource to check. Must be either "plugin" or "test". |
| `timestamp`      | `string` | **Required**. Name of item to fetch |
| `token` | `string` | **Required**. JWT token|

##### Example of request
```yaml
GET /notification/plugin/1745667165
Authorization: Bearer <token>
```

##### Example of response
```yaml
{
  "update": True
}
```

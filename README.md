

# ![NetStrikeLogo3](https://github.com/user-attachments/assets/00db6229-3905-4653-bfc0-c653079358ae)


NetStrike is a remote script manager based on a client-server architecture, where the server is responsible for executing scripts on demand from authenticated clients.

The project was initially developed for cybersecurity purposes, enabling the simulation of network attacks in a controlled environment.
Due to this focus, NetStrike has been built with a strong emphasis on security, featuring encryption, secure authentication (JWT), and input validation.

# Features
- Upload and manage scripts remotely

- Supported script types: .py, .sh, .ps1 (PowerShell support coming in future upgrades)

- Scheduled execution of scripts

- Secure communication over HTTPS

- User authentication via JWT

- Input and output sanitization to prevent injection attacks

- Role-based access control (future upgrade)

# Example - Script Templates
Scripts must implement a specific interface depending on the language.

Python script
```Python
class Script(Interface_Script):
    def __init__(self):
        self.params = []
        self.keys = ["reciver_email", "target_url", "seconds"]

    def execute(self):
        return "The actual script"

    def get_param(self):
        return self.keys

    def set_param(self, vet_param):
        try:
            self.params = []
            self.params.append(vet_param["reciver_email"])
            self.params.append(vet_param["target_url"])
            self.params.append(float(vet_param["seconds"]))
        except (ValueError, KeyError):
            return False
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

## Upload new script

```https
  GET /upload_script
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| Request body      | `dictionary` | **Required**. Contains the code of the script |

##### Example of request
```yaml
POST /upload_script
Authorization: Bearer <token>
{
    'content': 'class Script(Interface_Script):\n    def __init__(self):\n        self.params = []\n        self.keys = ["Ciao", "io", "sono", "giraffa"]\n\n    def execute(self):\n        # The actual script\n        return "Output"\n\n    def get_param(self):\n        return self.keys\n\n    def set_param(self, vet_param):\n        self.params = vet_param\n        return True\n',

    'name': 'fileTestBrutto.py'
}
```

##### Example of response
```yaml
{
    "message": "Plugin uploaded successfully"
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
    [
        {
            'id': 1,
            'name': "pythonScript.py"
        },
        {
            'id': 2,
            'name': "usefulTool.sh"
        }
    ]
}
```

## Get script description

```https
  GET /script_details/<script_id>
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `script_id`      | `integer` | **Required**. ID of the script |
| `token` | `string` | **Required**. JWT token|

##### Example of request
```yaml
GET /script_details/1
Authorization: Bearer <token>
```

##### Example of response
```yaml
{
  "description": "This script returns the status of every port in the specified range of the specified host.", 
  "params": ["ip_address", "start_port", "end_port"]
}
```

## Edit script

```https
  PATCH /edit_script/<script_id>
```

| Parameter | Type     | Description                       |
| `script_id`      | `integer` | **Required**. ID of the script |
| `token` | `string` | **Required**. JWT token|
| `name`      | `string` | **Required**. New name (set to None if it should not be changed) |
| `description`      | `string` | **Required**. New description (set to None if it should not be changed) |

##### Example of request
```yaml
PATCH /edit_script/2
Authorization: Bearer <token>

{
  "name": "newName",
  "description": "newDescription"
}
```


##### Example of response
```yaml
{}
```

## Remove script

```https
  DELETE /remove_script/<script_id>
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `script_id`      | `integer` | **Required**. ID of the script |
| `token` | `string` | **Required**. JWT token|

##### Example of request
```yaml
DELETE /remove_script/12
Authorization: Bearer <token>
```

##### Example of response
```yaml
{}
```

## Execute script
```https
  POST /execute/<script_id>
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `script_id`      | `integer` | **Required**. ID of the script |
| `token` | `string` | **Required**. JWT token|
| Request body      | `dictionary` | **Required**. Dictionary of parameters. The keys must match the expected names (see 'Get Script Description'). All parameters are required unless otherwise stated. |

##### Example of request
```yaml
POST /execute/3
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
  "success": true
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
    [
        {
            'id': 1
            'name': "2025-05-27 15:36:37"
        },
        {
            'id': 2
            'name': "2025-05-30 05:03:18"
        },
        {
            'id': 3
            'name': "2025-06-17 16:26:09"
        }
    ]
}
```

## Get test description

```https
  GET /test_details/<test_id>
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `test_id`      | `integer` | **Required**. ID of the test |
| `token` | `string` | **Required**. JWT token|

##### Example of request
```yaml
GET /test_details/3
Authorization: Bearer <token>
```

##### Example of response
```yaml
{
  "data": "2025-06-17 16:26:09",
  "result": "Output of pythonScript", 
  "success": true
}
```

## Create routine execution
```https
  POST /create_routine
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `token` | `string` | **Required**. JWT token|
| `script_id`      | `integer` | **Required**. ID of the script |
| `params` | `dictionary` | **Required**. Dictionary of script parameters. Keys must match those defined by the script (see 'Get Script Description'). All required parameters must be provided. |
| `frequency` | `integer` | **Required**. Interval in seconds between each scheduled execution |

##### Example of request
```yaml
POST /create_routine
Authorization: Bearer <token>

{
  "script_id": 4,
  "params":
  {
    "param1": "value",
    "param2": "value"
  },
  "frequency": 86400,
}
```

##### Example of response
```yaml
{}
```

## Checks for updates of the plugin list or test list

```https
  GET /notification/<timestamp>
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `timestamp`      | `string` | **Required**. Name of item to fetch |
| `token` | `string` | **Required**. JWT token|

##### Example of request
```yaml
GET /notification/1745667165
Authorization: Bearer <token>
```

##### Example of response
```yaml
{
  "update": True
}
```

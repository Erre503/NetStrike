
# NetStrike
![NetStrikeLogo3](https://github.com/user-attachments/assets/fb35bc1b-835b-4d34-9e95-103ee77d0b5b)
NetStrike is a remote script manager based on a client-server structure where the server executes the scripts when needed by the client.

The project was initially born for cyber-secuity purposes simulating attacks on a network, for this reason it is oriented to a secure dial structure  managing encryption and user autentication.

It is possible to upload scripts (python, powershell, bash) on the server that implements a specific interface: 



## Usage/Examples
Python script
```Python
class Plugin(Interfaccia_Plugin):
    def __init__(self):
        self.params = []
        self.keys = []

    def execute(self):
        return "Io sono stato caricato"

    def get_param(self):
        return self.keys

    def set_param(self, vet_param):
        self.params = vet_param
        return True
```
Bash script
```Bash
#!/bin/bash

message="Custom message"

set_param() {
    message="$1"
}

get_param() {
    echo "$message"
}

execute() {
    echo "Hello, World! $msg"
}

execute
```



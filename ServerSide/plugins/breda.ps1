

# File: esempio_plugin.ps1

# Funzione per ottenere i parametri
function get_param {
    Write-Output "ip, metodo, rangePorte, timeout"
}

# Funzione per impostare i parametri
function set_param {
    param (
        [string]$ip,
        [string]$metodo,
        [string]$rangePorte,
        [int]$timeout
    )
    $global:ip = $ip
    $global:metodo = $metodo
    $global:rangePorte = $rangePorte
    $global:timeout = $timeout
}

# Funzione principale di esecuzione
function execute {
    Write-Output "Esecuzione del plugin PowerShell con IP: $ip, Metodo: $metodo, RangePorte: $rangePorte, Timeout: $timeout"
}

# Gestione degli argomenti
if ($args[0] -eq "get_param") {
    get_param
} elseif ($args[0] -eq "execute") {
    execute
} else {
    Write-Output "Comando non riconosciuto."
}



    



    

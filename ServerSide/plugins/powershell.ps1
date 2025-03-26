param (
    [string]$Command = "",
    [string]$ip = "",
    [string]$metodo = "",
    [string]$rangePorte = "",
    [int]$timeout = 0
)
$paramFile = "$PSScriptRoot\params.json"

function get_param {
    Write-Output "ip, metodo, rangePorte, timeout"
}

function set_param {
    param (
        [string]$newIp,
        [string]$newMetodo,
        [string]$newRangePorte,
        [int]$newTimeout
    )
    $params = @{
        ip         = $newIp
        metodo     = $newMetodo
        rangePorte = $newRangePorte
        timeout    = $newTimeout
    }
    $params | ConvertTo-Json | Set-Content $paramFile
}

function execute {
    if (Test-Path $paramFile) {
        $params = Get-Content $paramFile | ConvertFrom-Json
        $ip = $params.ip
        $metodo = $params.metodo
        $rangePorte = $params.rangePorte
        $timeout = $params.timeout
        Write-Output "Eseguo scansione su $ip con metodo $metodo e range $rangePorte"
    }
}

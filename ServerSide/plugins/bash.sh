#!/bin/bash

# Variabili globali con valori di default
ip="127.0.0.1"
metodo="tcp"
rangePorte=("1" "10")
timeout="1"

# Funzione per impostare i parametri
function set_param {
    ip=$1
    metodo=$2
    IFS=',' read -ra rangePorte <<< "$3"
    timeout=$4
}

# Funzione per ottenere i parametri
function get_param {
    echo "$ip, $metodo, ${rangePorte[*]}, $timeout"
}

# Funzione principale di esecuzione del programma
function execute {
    echo "Esecuzione della scansione per l'IP $ip, Metodo: $metodo"
    echo "Range delle porte: ${rangePorte[@]}"
    echo "Timeout: $timeout"

    for port in "${rangePorte[@]}"; do
        echo "Scansione porta $port..."
    done
}

# Controllo dell'argomento passato
case "$1" in
    "set_param")
        set_param "$2" "$3" "$4" "$5"
        ;;
    "get_param")
        get_param
        ;;
    "execute")
        execute
        ;;
    *)
        echo "Comando non riconosciuto"
        ;;
esac


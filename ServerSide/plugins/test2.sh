#!/bin/bash

# Funzione per impostare i parametri
function set_param {
    ip=$1
    metodo=$2
    rangePorte=(${3//,/ })
    timeout=$4
}

# Funzione per ottenere i parametri
function get_param {
    echo "ip, metodo, rangePorte, timeout"
}

# Funzione principale di esecuzione del programma
function execute {
    echo "Esecuzione della scansione per l'IP $ip, Metodo: $metodo"
    echo "Range delle porte: ${rangePorte[@]}"
    echo "Timeout: $timeout"
    
    # Simula la scansione delle porte
    for port in "${rangePorte[@]}"; do
        echo "Scansione della porta $port..."
    done
}

# Esecuzione dello script
echo "Inizializzo il plugin Bash..."
set_param "192.168.1.1" "tcp" "22,80,443" 5
execute




    
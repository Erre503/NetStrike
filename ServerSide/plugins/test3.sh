#!/bin/bash

# Funzione per impostare i parametri
function set_param {
    ip=$1
    metodo=$2
    startPort=$3
    endPort=$4
    timeout=$5
}

# Funzione per ottenere i parametri
function get_param {
    echo "ip, metodo, startPort, endPort, timeout"
}

# Funzione principale di esecuzione del programma
function execute {
    echo "Esecuzione della scansione per l'IP $ip, Metodo: $metodo"
    echo "Intervallo delle porte: $startPort a $endPort"
    echo "Timeout: $timeout"

    # Simula la scansione delle porte
    for (( port=$startPort; port<=$endPort; port++ )); do
        if [[ $metodo == "tcp" ]]; then
            nc -zv -w $timeout $ip $port &>/dev/null
            if [ $? -eq 0 ]; then
                echo "Porta $port (TCP) è aperta."
            else
                echo "Porta $port (TCP) è chiusa."
            fi
        elif [[ $metodo == "udp" ]]; then
            nc -zvu -w $timeout $ip $port &>/dev/null
            if [ $? -eq 0 ]; then
                echo "Porta $port (UDP) è aperta."
            else
                echo "Porta $port (UDP) è chiusa."
            fi
        else
            echo "Metodo non valido. Usa 'tcp' o 'udp'."
            exit 1
        fi
    done
}

# Esecuzione dello script
echo "Inizializzo il plugin Bash..."
set_param "127.0.0.1" "tcp" 1 1024 1  # Intervallo da 1 a 1024 con timeout 1
execute





    
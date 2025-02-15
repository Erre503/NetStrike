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
    
    # Variabile per memorizzare le porte aperte
    open_ports=""

    # Simula la scansione delle porte
    for (( port=$startPort; port<=$endPort; port++ )); do
        if [[ $metodo == "tcp" ]]; then
            nc -zv -w $timeout $ip $port &>/dev/null
            if [ $? -eq 0 ]; then
                open_ports+="$port (TCP), "
            fi
        elif [[ $metodo == "udp" ]]; then
            nc -zvu -w $timeout $ip $port &>/dev/null
            if [ $? -eq 0 ]; then
                open_ports+="$port (UDP), "
            fi
        else
            echo "Metodo non valido. Usa 'tcp' o 'udp'."
            exit 1
        fi
    done

    # Rimuove l'ultima virgola e spazio (se ci sono porte aperte)
    if [ -n "$open_ports" ]; then
        open_ports=${open_ports%, }
        echo "Le porte aperte sono: $open_ports"
    else
        echo "Nessuna porta aperta trovata."
    fi
}

# Esecuzione dello script
echo "Inizializzo il plugin Bash..."
set_param "" "udp" 1 10 1  # Intervallo da 1 a 1024 con timeout 1
execute

    
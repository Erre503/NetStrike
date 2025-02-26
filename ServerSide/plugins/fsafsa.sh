
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
    
    # Inserisci qui la logica di scansione delle porte (come esempio)
    for port in "${rangePorte[@]}"; do
        echo "Scansione porta $port..."
    done
}


    

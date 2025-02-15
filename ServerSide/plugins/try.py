import socket  # serve per poter creare delle connessione con ad esempio udp e tcp
from interfaccia_plugin import Interfaccia_Plugin


class Plugin(Interfaccia_Plugin):
    #valori standard 
    ip = "127.0.0.1"  
    rangePorte = [1, 65535] 
    tipoScansione = 'TCP' 
    timeout = 1

    @classmethod
    def execute(cls):
        print("Esecuzione della scansione per l'IP " + cls.ip + ", Tipo:" + cls.metodo)
        porteAperte = scan_ports(cls.ip, cls.rangePorte, cls.metodo, cls.timeout)
        print("Porte aperte: " + str(porteAperte))


    @classmethod
    def get_param(cls):
        vet_param = [
            {'key': 'ip', 'description': 'Indirizzo IP da scansionare'},
            {'key': 'metodo', 'description': 'Metodo di scansione: TCP o UDP'},
            {'key': 'rangePorte', 'description': 'Range delle porte da scansionare'},
            {'key': 'timeout', 'description': 'Tempo massimo per tentare la connessione'}
        ]
        return vet_param
    
    @classmethod
    def set_param(cls, vet_param):
        cls.ip = vet_param['ip']
        cls.metodo = vet_param['metodo']
        cls.rangePorte = vet_param['rangePorte']
        cls.timeout = vet_param['timeout'] 
        return True
    

def scan_tcp(ip, porta, timeout):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Crea un oggetto TCP(i parametri indicano che e' ipv4 e tcp)
        sock.settimeout(timeout)  #funzione che imposta un tempo massimo per provare a connettersi alla porta
        result = sock.connect_ex((ip, porta))  # salva il tentativo di connessione nella porta in una variabile
        if result == 0:
            return "Porta " + str(porta) + " aperta"  # se e' 0 la connessione con la porta e' riuscita
        else:
            return "Porta " + str(porta) + " chiusa"
    except socket.error:
        return "Errore di connessione alla porta " + str(porta)
    finally:
        sock.close()  # Interrompe la connessione perche' non piu' necessaria


def scan_udp(ip, porta, timeout):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # dgram serve per avere un oggetto udp
        #sock.bind(('127.0.0.1', 12345))
        sock.settimeout(timeout) 
        sock.sendto(b'Hello', (ip, porta))  # invio 1 byte vuoto per verificare se la porta e' aperta
        sock.recvfrom(1024)  # funzione per ricevere il pacchetto ( parametro indica il massimo di byte ricevibili in 1 chiamata)
        return "Porta " + str(porta) + " aperta"
    except socket.error:
        return "Errore di connessione alla porta " + str(porta) + " (probabilmente chiusa)" #in caso scada il time out si da per chiusa la porta
    finally:
        sock.close()  


def scan_ports(ip, rangePorte, tipoScansione, timeout):
    porteAperte = [] 
    for porta in range(rangePorte[0], rangePorte[1] + 1): #il range esclude l'ultima porta, per questo +1
        if tipoScansione.lower() == 'tcp':  
            resScansione = scan_tcp(ip, porta, timeout)  
        elif tipoScansione.lower() == 'udp':  
            resScansione = scan_udp(ip, porta, timeout) 
        else:
            return "Erroe: il tipo di scansione non e' ne tcp ne udp"  # Se il tipo di scansione non è valido, restituisce un errore
        
        print(resScansione)  # Stampa il risultato della scansione per debug
        if "aperta" in resScansione:  
            porteAperte.append(porta)  
    
    return porteAperte 


    

    
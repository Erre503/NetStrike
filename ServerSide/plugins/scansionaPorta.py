import threading
import socket

def check_port(host, port):

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)  # Timeout di 1 secondo

    if sock.connect_ex((host, port)) == 0: # Restituisce 0 se la connessione è riuscita
        print(f"Porta {port}: Aperta")
    
    sock.close()

    

def execute(host, inizio, fine):
    print(f"Scansione porta dalla {inizio} alla {fine}")
    threads = []
    for port in range(inizio, fine+1):
        # Creazione di un thread per ogni porta
        thread = threading.Thread(target = check_port, args = (host, port))
        thread.daemon = True  # Imposta il thread come daemon: chiude il thread quando l'utente chiude il programma
        threads.append(thread) # Aggiunge il thread al vettore threads
        thread.start() # Esegue il thread

    # Aspetta che tutti i thread terminino
    for thread in threads:
        thread.join() # Termina il programma quando tutti i thread finiscono

    
    

execute("google.com", 1, 1)
    
    

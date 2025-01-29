import socket

def execute(host, port):
    print(f"Scansione porta {port} per {host} ")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  
    if sock.connect_ex((host, port)) == 0: # Restituisce 0 se la connessione è riuscita
        print(f"Porta {port} aperta")
    else:
        print(f"Porta {port} chiusa")

    sock.close()
    
execute("google.com", 81)

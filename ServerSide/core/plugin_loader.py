import os #libreria per poter lavorare con le cartelle e file dell'applicazione
import importlib #va a sostituire la funzione manuale di import dato che non siamo a conoscenza dei nomi dei file 
                 #e per rendere l'importazione dinamica
import sys  #serve per modificare a riga 38 i percorsi da cui prendere i file python
import abc
import inspect #serve per vedere i parametri
import subprocess #serve per eseguire comandi di sistema
import platform #serve per il multipiattaforma
import time #serve per operare con il tempo
from datetime import datetime #serve per l'ora esatta dei ping
import matplotlib.pyplot as plt #serve per creare il crafico dei ping
import smtplib #serve per inviare email via SMTP
from email.message import EmailMessage #usato per costruire l'email
from pathlib import Path #serve per ottenere il riferimento al percorso del file corrente

def get_plugin_type(nome_file):
    if nome_file.endswith('.sh'):
        return 'sh'
    if nome_file.endswith('.py'):
        return 'py'
    if nome_file.endswith('.ps1'):
        return 'ps1'
    return None

#crea una lista con tutti i file python all'interno della cartella
def lista_plugin(folder):  
    var = []
    for file in os.listdir(folder):
        if get_plugin_type(file) in ['sh', 'py', 'ps1']:
            var.append(file)
    return var

def cambiaNome(folder, nomeVecchio, nomeNuovo):
    try:
        trovato = False
        for file in os.listdir(folder):
            tipo = get_plugin_type(file)  # Ottieni il tipo del file
            if tipo and file[:-len(tipo)-1] == nomeVecchio:  
                vecchioFile = os.path.join(folder, file)
                nuovoFile = os.path.join(folder, nomeNuovo + "." + tipo)

                if os.path.exists(nuovoFile):
                    print("Errore: Il file "+nuovoFile+" esiste già.")
                    return False

                os.rename(vecchioFile, nuovoFile)
                print(f"File '{vecchioFile}' rinominato in '{nuovoFile}'")
                trovato = True
                break  # Interrompe il ciclo una volta trovato e rinominato il file

        if not trovato:
            print("Errore: Nessun file "+nomeVecchio+" trovato in "+folder)

        return trovato

    except Exception:
        print("Errore: impossibile rinominare il file.")
        return False


def avvia_plugin_ps1(nome_plugin, vet_param):
    try:
        percorso_file = folder / nome_plugin

        # Costruisci il comando per impostare i parametri
        set_comando = [
            "powershell",
            "-ExecutionPolicy", "Bypass",
            "-NoProfile",
            "-Command", f"& {{ . '{str(percorso_file)}'; set_param -newIp '{vet_param['ip']}' -newMetodo '{vet_param['metodo']}' -newRangePorte '{','.join(map(str, vet_param['rangePorte']))}' -newTimeout {vet_param['timeout']} }}"
        ]

        subprocess.run(set_comando, check=True, text=True, env=os.environ)

        # Ora esegui il plugin
        execute_comando = [
            "powershell",
            "-ExecutionPolicy", "Bypass",
            "-NoProfile",
            "-Command", f"& {{ . '{str(percorso_file)}'; execute }}"
        ]

        result = subprocess.run(execute_comando, capture_output=True, text=True, env=os.environ)

        print(f"Output PowerShell:\n{result.stdout}")
        if result.stderr:
            print(f"ERROR PowerShell:\n{result.stderr}")

    except Exception as e:
        print(f"Errore nell'esecuzione del plugin PowerShell: {e}")


def avvia_plugin_bash(plugin, vet_param):
    try:
        # Converti il percorso in stringa compatibile con Bash
        plugin = str(plugin)

        # Imposta i parametri con set_param
        bash_path = r"C:\Program Files\Git\bin\bash.exe"
        set_comando = [
            bash_path, plugin, "set_param",
            vet_param["ip"],
            vet_param["metodo"],
            ",".join(map(str, vet_param["rangePorte"])),
            str(vet_param["timeout"])
        ]
        subprocess.run(set_comando, check=True)

        # Ora esegui lo script Bash con 'execute'
        execute_comando = [bash_path, plugin, "execute"]
        result = subprocess.run(execute_comando, capture_output=True, text=True)

        # Output e gestione errori
        print(f"Output Bash:\n{result.stdout}")
        if result.stderr:
            print(f"ERROR Bash:\n{result.stderr}")

    except Exception as e:
        print(f"Errore nell'esecuzione del plugin Bash: {e}")



def avvia_plugin(nome_plugin, vet_param):
    tipo = get_plugin_type(nome_plugin)
    
    if tipo == 'py':
        try:
            modulo = importlib.import_module(nome_plugin[:-3])
            plugin_instance = modulo.Plugin()
            plugin_instance.set_param(vet_param)
            plugin_instance.execute()
        except Exception :
            print("Errore nell'importazione ed esecuzione del modulo Python")
    
    elif tipo == 'sh':
        percorso_file = folder / nome_plugin
        avvia_plugin_bash(percorso_file, vet_param)
    
    elif tipo == 'ps1':
        avvia_plugin_ps1(nome_plugin, vet_param)
    
    else:
        print("Tipo di plugin non supportato.")


def interfacciaBash(percorso_file):
    try:
        with open(percorso_file, 'r') as file: #apro il file e vedo se all'interno ci sono le funzioni richieste
            content = file.read()
            if "function set_param" not in content:
                print("Errore: La funzione 'set_param' non è presente nel plugin Bash.")
                return False
            if "function get_param" not in content:
                print("Errore: La funzione 'get_param' non è presente nel plugin Bash.")
                return False
            if "function execute" not in content:
                print("Errore: La funzione 'execute' non è presente nel plugin Bash.")
                return False
            return True
    except Exception:
        print("Errore nella lettura del file")
        return False
    
def interfacciaPs1(percorso_file):
    try:
        with open(percorso_file, 'r', encoding='utf-8') as file:
            content = file.read()
            if "function get_param" not in content:
                print("Errore: La funzione 'get_param' non è presente nel plugin PowerShell.")
                return False
            if "function set_param" not in content:
                print("Errore: La funzione 'set_param' non è presente nel plugin PowerShell.")
                return False
            if "function execute" not in content:
                print("Errore: La funzione 'execute' non è presente nel plugin PowerShell.")
                return False
            return True
    except Exception:
        print("Errore nella lettura del file PowerShell")
        return False


def creaPluginPy(nome_file, contenuto):

    #aggiungo l'estensione se il nome file non la ha
    if not nome_file.endswith('.py'):
        nome_file = nome_file + ".py"

    # Percorso della cartella 'plugins'
    folder = Path(__file__).resolve().parent.parent / "plugins"
    
    # Percorso completo del file
    percorso_file = os.path.join(folder, nome_file)

    # Controlla se il plugin esiste già
    if nome_file in os.listdir(folder):
        print("Nome del File già presente")
        return None

    #crea il file con il contenuto passato
    with open(percorso_file, "w", encoding="utf-8") as file:
        file.write(contenuto)
        print("File " + nome_file + " creato con successo nella cartella " + str(folder)) #stringa di debug
        print(" ") #crea uno spazio per rendere l'output più carino

    try:
        nome_plugin = nome_file[:-3]  # Rimuove l'estensione .py (verificata in precedenza)
        modulo = importlib.import_module(nome_plugin)
        
        # Verifica che esista un elemento 'Plugin' sia presente nel modulo
        if not hasattr(modulo, "Plugin"):
            print("Errore: Il file non contiene nessun elemento 'Plugin'.")
            os.remove(percorso_file)
            return False
        
        # Ottieni la presunta classe Plugin
        classe_plugin = getattr(modulo, "Plugin")
        
        # Verifica che 'Plugin' sia una classe
        if not inspect.isclass(classe_plugin):
            print("Errore: 'Plugin' non è una classe.")
            os.remove(percorso_file)
            return False
        
        #verifica che tutti i metodi astratti siano implementati
        if isinstance(classe_plugin, abc.ABCMeta):
            if hasattr(classe_plugin, '__abstractmethods__') and len(classe_plugin.__abstractmethods__) > 0:
                print("Errore: La classe 'Plugin' è astratta e non implementa tutti i metodi richiesti.")
                os.remove(percorso_file)
                return False
        if verifica_sintassi_python(percorso_file):
            return True
        else:
            print(percorso_file)
            print("errore sintassi errata")
            os.remove(percorso_file)
            return False

    except Exception:
        print("Errore: il Plugin non appartiene alla classe 'Plugin' ")
        os.remove(percorso_file)
        return False

def creaPluginSh(nome_file, contenuto):
    if not nome_file.endswith('.sh'):
        nome_file = nome_file + ".sh"
    
    folder = Path(__file__).resolve().parent.parent / "plugins"
    percorso_file = os.path.join(folder, nome_file)
    if nome_file in os.listdir(folder):
        print("Nome del File già presente")
        return False
    with open(percorso_file, "w", encoding="utf-8") as file:
        file.write(contenuto)
        print("File " + nome_file + " creato con successo nella cartella " + str(folder)) #stringa di debug
        print(" ") #crea uno spazio per rendere l'output più carino
    if interfacciaBash(percorso_file):
        if verifica_sintassi_bash(percorso_file):
            return True
        else:
            print("errore sintassi errata file sh")
            os.remove(percorso_file)
            return False
    else:
        print("il plugin non rispetta l'interfaccia")
        os.remove(percorso_file)
        return False

def creaPluginPs1(nome_file, contenuto):
    if not nome_file.endswith('.ps1'):
        nome_file = nome_file + ".ps1"

    folder = Path(__file__).resolve().parent.parent / "plugins"
    percorso_file = folder / nome_file

    if nome_file in os.listdir(folder):
        print("Nome del File già presente")
        return False

    with open(percorso_file, "w", encoding="utf-8") as file:
        file.write(contenuto)
        print("File "+nome_file+" creato con successo nella cartella "+str(folder))

    if interfacciaPs1(percorso_file):
        if verifica_sintassi_ps1(percorso_file):
            return True
        else:
            print("errore sintassi errata file ps1")
            os.remove(percorso_file)
            return False
    else:
        print("il plugin non rispetta l'interfaccia")
        os.remove(percorso_file)
        return False

    

def creaPlugin(nome_file, contenuto):
    if nome_file.endswith('.sh'):
        return creaPluginSh(nome_file, contenuto)
    if nome_file.endswith('.py'):
        return creaPluginPy(nome_file, contenuto)
    if nome_file.endswith('.ps1'):
        return creaPluginPs1(nome_file, contenuto)
    print("Il tipo di file non e' supportato")
    return None

def verifica_sintassi_python(percorso_file):
    try:
        subprocess.run(['python3', '-m', 'py_compile', percorso_file], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Il file ha una sintassi corretta.")
        return True
    except subprocess.CalledProcessError:
        print("Errore di sintassi nel file.")
        return False
    
def verifica_sintassi_bash(percorso_file):
    bash_path = r"C:\Program Files\Git\bin\bash.exe"
    try:
        subprocess.run([bash_path, '-n', str(percorso_file)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Il file ha una sintassi corretta.")
        return True
    except subprocess.CalledProcessError:
        print("Errore di sintassi nel file.")
        return False
    
def verifica_sintassi_ps1(percorso_file):
    try:
        comando = ["powershell", "-NoProfile", "-NonInteractive", "-Command", f"Get-Content '{str(percorso_file)}' | Out-String | Invoke-Expression"]
        subprocess.run(comando, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Il file PowerShell ha una sintassi corretta.")
        return True
    except subprocess.CalledProcessError:
        print("Errore di sintassi nel file PowerShell")
        return False

    
def estraiParametriBash(plugin):
    bash_path = r"C:\Program Files\Git\bin\bash.exe"
    try:
        comando = [bash_path, plugin, "get_param"]  
        parametri = subprocess.run(comando, capture_output=True, text=True, check=True)
        listaParametri = parametri.stdout.strip().split(", ")  
        
        if len(listaParametri) < 4:
            print("Errore: parametri incompleti ricevuti da Bash")
            return None

        return {
            "ip": listaParametri[0],
            "metodo": listaParametri[1],
            "rangePorte": list(map(int, listaParametri[2].split())),
            "timeout": int(listaParametri[3])
        }
    except Exception as e:
        print("Errore nell'estrazione dei parametri Bash:", e)
        return None

def estraiParametriPs1(plugin):
    try:
        comando = [
            "powershell",
            "-ExecutionPolicy", "Bypass",
            "-NoProfile",  
            "-Command", f"& {{ . '{str(plugin)}'; get_param }}"
        ]
        parametri = subprocess.run(comando, capture_output=True, text=True)


        if parametri.returncode != 0:
            print(f"Errore durante l'esecuzione del plugin: codice {parametri.returncode}")
            return None
        
        listaParametri = parametri.stdout.strip().split("\n")[-1].strip().split(", ")
        return listaParametri
    except Exception as e:
        print(f"Errore nell'estrazione dei parametri PowerShell: {e}")
        return None
    
def elimina_file(folder,nome_file):
    try:
        trovato = False
        percorso_file = folder / nome_file
        for file in os.listdir(folder):
            if file == nome_file:  
                trovato = True
                os.remove(percorso_file)
                break  

        if not trovato:
            print("Errore: Nessun file "+nome_file+" trovato in "+folder)

        return trovato

    except Exception:
        print("Errore: impossibile cancellare il file.")
        return False

def monitoraggio_server(email,url,tempo_monitoraggio):
    intervallo_ping = 3  # ogni N secondi fa un ping , per ora 3
    max_fail = 2  # ogni N tentativi manda l'avviso, per ora 2
    fail_count = 0  # contatore di ping falliti per fermare poi il ciclo
    dati_ping = []  # salva il futuro output
    start_time = time.time()  # orario di inizio del monitoraggio

    # loop che continua finché non finisce il tempo di monitoraggio o N tentativi falliscono
    while (time.time() - start_time) < tempo_monitoraggio: #time.time() da l'orario in quel momento
        try:
            # comando diverso a seconda del sistema operativo
            if platform.system().lower() == "windows":
                comando = ["ping", "-n", "1", url]
            else:
                comando = ["ping", "-c", "1", url] #linux e ios

            # esegue il ping con il comando salvato prima e salva il risultato
            result = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            if result.returncode == 0:  # se vero il ping è riuscito
                output = result.stdout  # prendiamo l’output del ping
                if platform.system().lower() == "windows": # comando diverso a seconda del sistema operativo
                    for line in output.splitlines():  # scorriamo ogni riga
                        if "durata=" in line:
                            time_part = line.split("durata=")[1].split("ms")[0].strip()
                            ping_ms = float(time_part)
                            break
                        elif "time=" in line:
                            time_part = line.split("time=")[1].split("ms")[0].strip()
                            ping_ms = float(time_part)
                            break
                    else:
                        ping_ms = None
                else:
                    for line in output.splitlines():
                        if "time=" in line:
                            ping_ms = float(line.split("time=")[1].split(" ")[0])  
                            break
                    else:
                        ping_ms = None
                #fail_count = 0   reset se il ping è ok???
            else:
                ping_ms = None  # ping fallito
                fail_count += 1  
                
        except Exception as e:  # errore nel ping
            ping_ms = None
            fail_count += 1

        oraPing = datetime.now()  # orario esatto del ping
        dati_ping.append((oraPing, ping_ms))  #salvo ora e tempo del ping

        if fail_count >= max_fail:
            invioEmailAvviso(email, url)  # se ha fallito troppe volte, manda avviso
            break

        time.sleep(intervallo_ping)  # aspetta prima del prossimo ping

    # dopo il monitoraggio manda il grafico via email
    invioGrafico(email, dati_ping, url)
    return dati_ping  # ritorna i dati raccolti 

def invioGrafico(email, dati, url):
    x = [d[0] for d in dati if d[1] is not None]  # orari dei ping riusciti
    y = [d[1] for d in dati if d[1] is not None]  # valori dei ping riusciti

    # crea il grafico
    plt.figure(figsize=(10, 5))
    plt.plot(x, y, marker='o')
    plt.title(f'Ping Monitor - {url}')
    plt.xlabel('Orario')
    plt.ylabel('Ping (ms)')
    plt.grid(True)
    plt.xticks(rotation=45)

    # salva il grafico come immagine
    img_path = os.path.join(os.getcwd(), 'ping_graph.png')
    plt.tight_layout()
    plt.savefig(img_path)
    plt.close()

    # prepara l’email con l’allegato
    msg = EmailMessage()
    msg['Subject'] = f'Grafico Monitoraggio - {url}'
    msg['From'] = 'nicolacasagrande54@gmail.com'
    msg['To'] = email
    msg.set_content('In allegato il grafico con i risultati del monitoraggio.')

    # allega l’immagine
    with open(img_path, 'rb') as f:
        img_data = f.read()
        msg.add_attachment(img_data, maintype='image', subtype='png', filename='ping_graph.png')

    # invia l’email con l’allegato
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login('nicolacasagrande54@gmail.com', 'nizh qsff zgzv zasd')
        smtp.send_message(msg)

def invioEmailAvviso(email, url):
    msg = EmailMessage()  # crea una nuova email
    msg['Subject'] = f'⚠️ Server Offline - {url}'  # oggetto dell’email
    msg['From'] = 'nicolacasagrande54@gmail.com'  # mittente (puoi cambiarlo)
    msg['To'] = email  # destinatario
    msg.set_content(f'Il server {url} è stato rilevato come offline.')  # contenuto del messaggio

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:  # connessione al server SMTP
        smtp.starttls()  # cifratura della connessione
        smtp.login('nicolacasagrande54@gmail.com', 'nizh qsff zgzv zasd')  # login al server
        smtp.send_message(msg)  # invia l’email

if(__name__ == "__main__"):
    print("Quale file PY vuoi eseguire?")
    folder = Path(__file__).resolve().parent.parent / "plugins"  # assegna il percorso della cartella basandosi su quello del plugin loader
                                                                 #(Path(__file__).resolve()) per avere il percorso assoluto
    sys.path.append(str(folder))  #aggiunge la cartella folder ai percorsi da cui vengono importati i file python
    # Carica i nomi dei plugin presenti
    for i in lista_plugin(folder): 
        print(i)
    nome_plugin = input() #il nome per fare i test è dato in input
    
    #esempio plugin
    contenuto = """import socket  # serve per poter creare delle connessione con ad esempio udp e tcp
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
            return "Errore: il tipo di scansione non e' ne tcp ne udp"  # Se il tipo di scansione non è valido, restituisce un errore
        
        print(resScansione)  # Stampa il risultato della scansione per debug
        if "aperta" in resScansione:  
            porteAperte.append(porta)  
    
    return porteAperte 

"""

    
    creazione = creaPlugin(nome_plugin, contenuto)#salva il modulo(il file)
    if creazione:#se è None non provo ad eseguire il plugin
        if get_plugin_type(nome_plugin) == 'sh':
            plugin= folder / nome_plugin
            parametri = estraiParametriBash(plugin)  # Estrai i parametri dal file Bash
            print("Parametri del plugin Bash:" + str(parametri))
            vet_param = {
                "ip": "127.0.0.1", 
                "metodo": "tcp",   
                "rangePorte" : [1, 10] , 
                "timeout": 1         
            }
            avvia_plugin(nome_plugin, vet_param) 
        if get_plugin_type(nome_plugin) == 'py':
            modulo = importlib.import_module(nome_plugin[:-3])  # Rimuove ".py"
            plugin = modulo.Plugin()
            parametri = plugin.get_param()
            key_values = []
            for parametro in parametri:
                key_values.append(parametro['key'])
            vet_param = {
                        key_values[0]: '127.0.0.1',        # ip
                        key_values[1]: 'tcp',              # metodo di scansione
                        key_values[2]: [1,10],         # rangePorte
                        key_values[3]: 1                   # timeout
            }
            avvia_plugin(nome_plugin, vet_param)
        if get_plugin_type(nome_plugin) == 'ps1':
            plugin = folder / nome_plugin
            parametri = estraiParametriPs1(plugin)
            print("Parametri del plugin PowerShell: " ,parametri)
            vet_param = {
                "ip": "127.0.0.1", 
                "metodo": "tcp",   
                "rangePorte" : [1, 10] , 
                "timeout": 1         
            }
            avvia_plugin(nome_plugin, vet_param)
        email = "nicolacasagrande54@gmail.com"
        url = "google.com"  
        tempo_monitoraggio = 15 

        # Avvia la funzione
        dati_ping = monitoraggio_server(email, url, tempo_monitoraggio)

        # Mostra i dati raccolti
        print("\n--- RISULTATI ---")
        for dt, ping in dati_ping:
            print(f"{dt.strftime('%H:%M:%S')} -> {ping} ms")
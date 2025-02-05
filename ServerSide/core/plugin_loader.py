import os #libreria per poter lavorare con le cartelle e file dell'applicazione
import importlib #va a sostituire la funzione manuale di import dato che non siamo a conoscenza dei nomi dei file 
                 #e per rendere l'importazione dinamica
import sys  #serve per modificare a riga 38 i percorsi da cui prendere i file python

from pathlib import Path #serve per ottenere il riferimento al percorso del file corrente

def caricaPlugin(): #folder e req si possono dichiarare come variabili globale se necessario
                                            #(il diagramma dice di passargli solo nome_plugin)

    folder = Path(__file__).resolve().parent.parent / "plugins"
    req = "execute"

    print("Quale file PY vuoi eseguire?")
    nome_plugin = input() #il nome per fare i test e' dato in input

    if(nome_plugin.endswith('.py')):
        nome_plugin = nome_plugin[:-3]

    guardia = False
    for file in os.listdir(folder): #il for verifica tutti i file all'interno della cartella
        if nome_plugin == file[:-3] and file.endswith('.py'): #verifica se il file e' python e se corrisponde a quello cercato,altrimenti passa al prossimo
            modulo = importlib.import_module(nome_plugin) #importa il file python cercato nella variabile modulo
            guardia = True

    if(guardia):
        return modulo
    else:
        print("File NON trovato")
        return None

def lista_plugin(): #crea una lista con tutti i file python all'interno della cartella
    vet = []
    folder = Path(__file__).resolve().parent.parent / "plugins"
    for file in os.listdir(folder):
        if file[:-3] and file.endswith('.py'):
            vet.append(file)
    return vet

def avvia_plugin(): #funzione del diagramma richiesta per avviare il plugin
    plugin.execute()


def creaPlugin(nome_file, contenuto):

    if not nome_file.endswith('.py'):
        nome_file = nome_file + ".py"

    req = "def execute():"

    # Percorso della cartella 'plugins'
    folder = Path(__file__).resolve().parent.parent / "plugins"
    
    # Percorso completo del file
    percorso_file = os.path.join(folder, nome_file)

    #Controllo se il plugin rispetta i requisiti
    guardia = True
    for file in os.listdir(folder):
        if nome_file == file and file.endswith('.py'):
            guardia = False

    if(guardia):
        if req in contenuto:
            #getattr prende l'attributo desiderato(req) dal modulo(il file), se non esiste ritorna None, poi verifica che sia una
            #funzione con callable il quale prova a chiamarla
            with open(percorso_file, "w", encoding="utf-8") as file:
                file.write(contenuto)
            return "File " + nome_file + " creato con successo nella cartella plugins"
        else:
            return "Errore: il file non rispetta i requisiti: " + req
    else: 
        return "Nome del File già presente"



if(__name__ == "__main__"):
    folder = Path(__file__).resolve().parent.parent / "plugins"  # assegna il percorso della cartella basandosi su quello del plugin loader
                                                                 #(Path(__file__).resolve()) per avere il percorso assoluto
    sys.path.append(str(folder))  #aggiunge la cartella folder ai percorsi da cui vengono importati i file python

    print("Nome del Plug In da creare: ")
    nome = input()
    print(creaPlugin(nome, "def execute(): print(2)"))

    # Carica i nomi dei plugin presenti
    for i in lista_plugin(): 
        print(i)

    plugin = caricaPlugin() #viene caricato il modulo del file richiesto in una variabile per poter essere eseguita

    if(plugin!=None):#se e' None non provo ad eseguire il plugin
        avvia_plugin()

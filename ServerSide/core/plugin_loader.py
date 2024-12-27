import os #libreria per poter lavorare con le cartelle e file dell'applicazione
import importlib #va a sostituire la funzione manuale di import dato che non siamo a conoscenza dei nomi dei file 
                 #e per rendere l'importazione dinamica
import sys  #serve per modificare a riga 38 i percorsi da cui prendere i file python

from pathlib import Path #serve per ottenere il riferimento al percorso del file corrente

def caricaPlugin(folder, req, nome_plugin): #folder e req si possono dichiarare come variabili globale se necessario
                                            #(il diagramma dice di passargli solo nome_plugin)

    for file in os.listdir(folder): #il for verifica tutti i file all'interno della cartella
        if nome_plugin == file[:-3] and file.endswith('.py'): #verifica se il file e' python e se corrisponde a quello cercato,altrimenti passa al prossimo

            modulo = importlib.import_module(nome_plugin) #importa il file python cercato nella variabile modulo
            
            if callable(getattr(modulo, req, None)):
                #getattr prende l'attributo desiderato(req) dal modulo(il file), se non esiste ritorna None, poi verifica che sia una
                #funzione con callable il quale prova a chiamarla

                return modulo  # salvo il plugin se ha tutti i requisiti richiesti
            else:
                print("Errore: il file non rispetta i requisiti per essere avviato")
                return None
    print("Errore: il file non e' stato trovato all'interno della cartella")
    return  None

def lista_plugin(folder): #crea una lista con tutti i file python all'interno della cartella
    var = []
    for file in os.listdir(folder):
        if file[:-3] and file.endswith('.py'):
            var.append(file)
    return var

def avvia_plugin(): #funzione del diagramma richiesta per avviare il plugin
    plugin.execute()
    return 

if(__name__ == "__main__"):
    print("Quale file PY vuoi eseguire?")
    nome_plugin = input() #il nome per fare i test e' dato in input
    req = "execute" # Requisiti: la funzione 'esegui' deve essere presente
    folder = Path(__file__).resolve().parent.parent / "plugins"  # assegna il percorso della cartella basandosi su quello del plugin loader
                                                                 #(Path(__file__).resolve()) per avere il percorso assoluto
    sys.path.append(str(folder))  #aggiunge la cartella folder ai percorsi da cui vengono importati i file python

    # Carica i nomi dei plugin presenti
    for i in lista_plugin(folder): 
        print(i)

    plugin = caricaPlugin(folder, req, nome_plugin) #viene caricato il modulo del file richiesto in una variabile per poter essere eseguita

    if(plugin!=None):#se e' None non provo ad eseguire il plugin
        avvia_plugin()
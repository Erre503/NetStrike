import tkinter as tk
from tkinter import filedialog, messagebox
import os

""" CLASSE DELLA GUI """
class MainInterfaccia(tk.Frame):
    def __init__(self, finestraPrincipale, coreApplicazione):
        super().__init__(finestraPrincipale)  # X inizializzare il frame "finestraPrincipale"
        self.finestraPrincipale = finestraPrincipale  # X riferirsi al frame 
        self.coreApplicazione = coreApplicazione  # X collegamento al core
        self.initUI()  # X definire la gui

    """ GLI ELEMENTI DELLA GUI """
    def initUI(self):
        self.finestraPrincipale.title("PlugInc")  # x il titolo della finestra
        self.finestraPrincipale.geometry("1000x1000")  # X la dimesione della finestra

        """ BOTTONE LOAD """
        self.bottoneLoad = tk.Button(self, text="LOAD", command=self.caricaPlugin)
        self.bottoneLoad.pack(pady=10)  # x aggiungere load alla gui

        """ BOTTONE CLEAR """
        self.bottoneClear = tk.Button(self, text="CLEAR", command=self.pulisciPlugin)
        self.bottoneClear.pack(pady=10) # ...

        """ BOX DEI PLUGIN CARICATI """
        self.listaPlugin = tk.Listbox(self, selectmode=tk.SINGLE, width=50, height=10)
        self.listaPlugin.pack(pady=10) # x aggiungere il box alla gui
        self.listaPlugin.bind("<Double-1>", self.dettagliPlugin) # x fare il doppio click

        """ DETTAGLI DEL TEST """
        self.testoDettagli = tk.Text(self, height=5, wrap=tk.WORD)
        self.testoDettagli.pack(pady=10, fill=tk.X) # ...

        """ BOTTONE CONFIGURE """
        self.bottoneConfigure = tk.Button(self, text="Configure", command=self.configuraPlugin)
        self.bottoneConfigure.pack(pady=10) # ...

        """ BOTTONE START """
        self.bottoneStart = tk.Button(self, text="START", command=self.iniziaTest)
        self.bottoneStart.pack(pady=10) # ...

        self.pack()  # x mettere il frame nella gui

        """ FUNZIONE X LA BOX DEI PLUGIN """
        self.aggiornaListaPlugin()

    """ FUNZIONE X PRENDERE LISTA E AGGIORNARLA """
    def aggiornaListaPlugin(self):
        self.listaPlugin.delete(0, tk.END)  # X vedere solo i plugin attualmente caricati
        nomiPlugin = self.coreApplicazione.PluginList()  # X prendere la lista dal Core
        for nome in nomiPlugin:  # X inserire i nomi dei plugin nella box
            self.listaPlugin.insert(tk.END, nome)

    """ FUNZIONE X APRIRE GESTIONE FILE E SELEZIONARE IL FILE """
    def caricaPlugin(self):
        percorsoFile = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if percorsoFile:  # Se un file viene selezionato dall'utente
            try:
                self.coreApplicazione.carPlugin(percorsoFile)  # X caricare il plugin dal Core
                self.aggiornaListaPlugin()
            except Exception as e:
                messagebox.showerror("Error", f"Errore nel caricamento: {e}")  # X mostrare un errore se qualcosa non va

    """ FUNZIONE X RIMUOVERE I PLUGIN """
    def pulisciPlugin(self):
        try:
            self.coreApplicazione.rimuoviPlugin()  # X rimuovere i plugin dal Core
            self.aggiornaListaPlugin()
        except Exception as e:
            messagebox.showerror("Error", f"Errore nella rimozione: {e}")  # X mostrare un errore se qualcosa non va

    """ FUNZIONE X MOSTRARE I DETTAGLI DEL PLUGIN """
    def dettagliPlugin(self, event):
        pluginSelezionato = self.listaPlugin.get(self.listaPlugin.curselection())  # X ottenre il plugin selezionato
        dettagliPlugin = self.coreApplicazione.ottieniDettagli(pluginSelezionato)  # Ottiene i dettagli dal core
        self.testoDettagli.delete(1.0, tk.END)  # Pulisce la TextBox dei dettagli
        self.testoDettagli.insert(tk.END, dettagliPlugin)  # Inserisce i dettagli del plugin nella TextBox

    """ FUNZIONE X CONFIGURARE I DETTAGLI DEL PLUGIN """
    def configuraPlugin(self):
        pluginSelezionato = self.listaPlugin.get(self.listaPlugin.curselection())  # ...
        if pluginSelezionato:
            finestraConfig = tk.Toplevel(self)  # X creare una finestra secondaria
            finestraConfig.title(f"Configurazione di: {pluginSelezionato}")  # X il titolo della finestra
            finestraConfig.geometry("350x350")  # X la dimesione della finestra

            tk.Label(finestraConfig, text="Parametro del test:").pack(pady=10)  # Label x il parametro da inserire
            parametriInseriti = tk.Entry(finestraConfig, width=30)  # X scrivere il valore del parametro
            parametriInseriti.pack(pady=10) # ...

            """ FUNZIONE X INVIARE AL CORE LA CONFIGURAZIONE """
            def inviaConfigurazione():
                parametriTest = parametriInseriti.get()  # Ottiene il valore del parametro dal campo di testo
                try:
                    self.coreApplicazione.confPlugin(pluginSelezionato, parametriTest)  # X configurare il plugin dal core
                    finestraConfig.destroy()  # X chiudere la finestra
                except Exception as e:
                    messagebox.showerror("Error", f"Errore nella configurazione: {e}")  # X mostrare un errore se qualcosa non va

            """ BOTTONE X INVIARE AL CORE LA CONFIGURAZIONE """
            tk.Button(finestraConfig, text="Submit", command=inviaConfigurazione).pack(pady=10)

    """ FUNZIONE X AVVIARE IL TEST """
    def iniziaTest(self):
        pluginSelezionato = self.listaPlugin.get(self.listaPlugin.curselection())  # ...
        if pluginSelezionato:
            try:
                risultatoTest = self.core.startPlugin(pluginSelezionato)  # X iniziare il test dal core
                messagebox.showinfo("Test Result", f"RISULTATO: {risultatoTest}")  # X mostrare l'output
            except Exception as e:
                messagebox.showerror("Error", f"Errore nell'inzializzazione del test: {e}")  # X mostrare un errore se qualcosa non va


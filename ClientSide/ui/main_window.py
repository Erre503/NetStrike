import tkinter as tk
from tkinter import filedialog, messagebox
import os

class MainInterfaccia(tk.Frame):
    def __init__(self, finestraPrincipale, coreApplicazione):
        super().__init__(finestraPrincipale)
        self.finestraPrincipale = finestraPrincipale
        self.coreApplicazione = coreApplicazione
        self.initUI()

    def initUI(self):
        self.finestraPrincipale.title("PlugInc")
        self.finestraPrincipale.geometry("1000x1000")

        self.bottoneLoad = tk.Button(self, text="LOAD", command=self.caricaPlugin)
        self.bottoneLoad.pack(pady=10)

        self.bottoneClear = tk.Button(self, text="CLEAR", command=self.pulisciPlugin)
        self.bottoneClear.pack(pady=10)

        self.listaPlugin = tk.Listbox(self, selectmode=tk.SINGLE, width=50, height=10)
        self.listaPlugin.pack(pady=10)
        self.listaPlugin.bind("<Double-1>", self.dettagliPlugin)

        self.testoDettagli = tk.Text(self, height=5, wrap=tk.WORD)
        self.testoDettagli.pack(pady=10, fill=tk.X)

        self.bottoneConfigure = tk.Button(self, text="Configure", command=self.configuraPlugin)
        self.bottoneConfigure.pack(pady=10)

        self.bottoneStart = tk.Button(self, text="START", command=self.iniziaTest)
        self.bottoneStart.pack(pady=10)

        self.pack()
        # DEBUG self.aggiornaListaPlugin()

    def aggiornaListaPlugin(self):
        self.listaPlugin.delete(0, tk.END)
        # Assuming you have a method in ClientCore to get the list of plugins
        nomiPlugin = self.coreApplicazione.ottieni_lista_plugin()  # Update this line
        for nome in nomiPlugin:
            self.listaPlugin.insert(tk.END, nome)

    def caricaPlugin(self):
        percorsoFile = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if percorsoFile:
            try:
                self.coreApplicazione.aggiungi_plugin(percorsoFile)  # Update this line
                self.aggiornaListaPlugin()
            except Exception as e:
                messagebox.showerror("Error", f"Errore nel caricamento: {e}")

    def pulisciPlugin(self):
        try:
            self.coreApplicazione.rimuovi_plugin()  # Update this line
            self.aggiornaListaPlugin()
        except Exception as e:
            messagebox.showerror("Error", f"Errore nella rimozione: {e}")

    def dettagliPlugin(self, event):
        pluginSelezionato = self.listaPlugin.get(self.listaPlugin.curselection())
        dettagliPlugin = self.coreApplicazione.ottieni_dettagli_plugin(pluginSelezionato)  # Update this line
        self.testoDettagli.delete(1.0, tk.END)
        self.testoDettagli.insert(tk.END, dettagliPlugin)

    def configuraPlugin(self):
        pluginSelezionato = self .listaPlugin.get(self.listaPlugin.curselection())
        if pluginSelezionato:
            finestraConfig = tk.Toplevel(self)
            finestraConfig.title(f"Configurazione di: {pluginSelezionato}")
            finestraConfig.geometry("350x350")

            tk.Label(finestraConfig, text="Parametro del test:").pack(pady=10)
            parametriInseriti = tk.Entry(finestraConfig, width=30)
            parametriInseriti.pack(pady=10)

            def inviaConfigurazione():
                parametriTest = parametriInseriti.get()
                try:
                    self.coreApplicazione.configura_plugin(pluginSelezionato, parametriTest)  # Update this line
                    finestraConfig.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Errore nella configurazione: {e}")

            tk.Button(finestraConfig, text="Submit", command=inviaConfigurazione).pack(pady=10)

    def iniziaTest(self):
        pluginSelezionato = self.listaPlugin.get(self.listaPlugin.curselection())
        if pluginSelezionato:
            try:
                parametriTest = {}  # You may want to collect parameters from the UI
                risultatoTest = self.coreApplicazione.avvia_test(pluginSelezionato, parametriTest)  # Update this line
                messagebox.showinfo("Test Result", f"RISULTATO: {risultatoTest}")
            except Exception as e:
                messagebox.showerror("Error", f"Errore nell'inizializzazione del test: {e}")

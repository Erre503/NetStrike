import tkinter as tk
from tkinter import filedialog, messagebox

class MainInterfaccia(tk.Frame):
    def __init__(self, finestraPrincipale, coreApplicazione):
        super().__init__(finestraPrincipale)
        self.finestraPrincipale = finestraPrincipale
        self.coreApplicazione = coreApplicazione
        self.plugin_files = {}  # Dictionary to store plugin names and their file paths and IDs

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
        self.aggiornaListaPlugin()

    def aggiornaListaPlugin(self):
        self.listaPlugin.delete(0, tk.END)
        self.coreApplicazione.ottieni_lista_plugin()

    def caricaPlugin(self):
        percorsoFile = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if percorsoFile:
            try:
                # Assuming the ID is generated or retrieved from the core application
<<<<<<< Updated upstream
                plugin_id = self.coreApplicazione.aggiungi_plugin(percorsoFile)  # This should return the ID
                plugin_name = percorsoFile.split('/')[-1]  # Get the file name
                # Store the file path and ID in the dictionary
                self.plugin_files[plugin_name] = {'id': plugin_id}
                self.aggiornaListaPlugin()
=======
                self.coreApplicazione.aggiungi_plugin(percorsoFile)  # This should return the ID
>>>>>>> Stashed changes
            except Exception as e:
                messagebox.showerror("Error", f"Errore nel caricamento: {e}")

    def pulisciPlugin(self):
        try:
            self.coreApplicazione.rimuovi_plugin()
            self.aggiornaListaPlugin()
        except Exception as e:
            messagebox.showerror("Error", f"Errore nella rimozione: {e}")

    def dettagliPlugin(self, event):
        pluginSelezionato = self.listaPlugin.get(self.listaPlugin.curselection())
        # Retrieve the file path and ID using the selected plugin name
        plugin_info = self.plugin_files.get(pluginSelezionato)
        if plugin_info:
            plugin_id = plugin_info['id']
            # Assuming you have a method to get details based on the file path
<<<<<<< Updated upstream
            dettagli = self.coreApplicazione.ottieni_dettagli_plugin((str)(plugin_id))  # Use the ID to get details
            # Display the details
            self.mostra_dettagli_plugin(plugin_id, dettagli['description'], dettagli['parameters'])
=======
            self.coreApplicazione.ottieni_dettagli_plugin((str)(plugin_id))  # Use the ID to get details
>>>>>>> Stashed changes
        else:
            messagebox.showerror("Error", "No details found for the selected plugin.")

    def configuraPlugin(self):
        pluginSelezionato = self.listaPlugin.get(self.listaPlugin.curselection())
        if pluginSelezionato:
            finestraConfig = tk.Toplevel(self)
            finestraConfig.title(f"Configurazione di: {pluginSelezionato}")
            finestraConfig.geometry("350x350")

            tk.Label(finestraConfig, text="Parametro del test:").pack(pady=10)
            parametriInseriti = tk.Entry(finestraConfig, width=30)
            parametriInseriti.pack(pady=10)

    def iniziaTest(self):
        pluginSelezionato = self.listaPlugin.get(self.listaPlugin.curselection())
        if pluginSelezionato:
            try:
<<<<<<< Updated upstream
=======
                print(self.plugin_files)
>>>>>>> Stashed changes
                plugin_info = self.plugin_files.get(pluginSelezionato)
                if plugin_info:
                    plugin_id = plugin_info['id']
                    parametriTest = {}  # You may want to collect parameters from the UI
                    self.coreApplicazione.avvia_test((str)(plugin_id), parametriTest)
            except Exception as e:
                messagebox.showerror("Error", f"Errore nell'inizializzazione del test: {e}")

    def svuota_lista_plugin(self):
        self.listaPlugin.delete(0, tk.END)

    def aggiungi_plugin(self, name, plugin_id):
        self.listaPlugin.insert(tk.END, name)
        self.plugin_files[name] = {'id': plugin_id}

    def mostra_dettagli_plugin(self, description, parameters):
        self.testoDettagli.delete(1.0, tk.END)
        dettagli = f"Description: {description}\nParameters: {parameters}"
        self.testoDettagli.insert(tk.END, dettagli)

    def mostra_risultato_test(self, status, log, datetime):
        messagebox.showinfo("Test Result", f"Status: {status}\nLog: {log}\nDateTime: {datetime}")
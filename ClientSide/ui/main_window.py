import customtkinter as ctk
from tkinter import filedialog, messagebox
from core.core import ClientCore  # Importa il core dell'applicazione

class MainInterfaccia(ctk.CTkFrame):
    def __init__(self, finestraPrincipale, coreApplicazione):
        super().__init__(finestraPrincipale)
        self.finestraPrincipale = finestraPrincipale
        self.coreApplicazione = coreApplicazione
        self.plugin_files = {} 
        self.plugin_selezionato = None
        self.initUI()

    def initUI(self):
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")

        self.finestraPrincipale.title("PlugInk")
        self.finestraPrincipale.geometry("1000x650")
        self.finestraPrincipale.resizable(False, False)

        self.frameSX = ctk.CTkFrame(self.finestraPrincipale, width=400, height=600)
        self.frameSX.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.frameDX = ctk.CTkFrame(self.finestraPrincipale, width=400, height=600)
        self.frameDX.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.finestraPrincipale.grid_columnconfigure(0, weight=1)
        self.finestraPrincipale.grid_columnconfigure(1, weight=1)
        self.finestraPrincipale.grid_rowconfigure(0, weight=1)

        self.labelCaricaP = ctk.CTkLabel(self.frameSX, text="LOAD PLUG-IN", font=("Felix Titling", 40))
        self.labelCaricaP.pack(pady=10)

        self.bottoneCaricaP = ctk.CTkButton(self.frameSX, text="BROWSE", corner_radius=5, command=self.caricaPlugin)
        self.bottoneCaricaP.pack(pady=10)

        self.labelPSelezionabili = ctk.CTkLabel(self.frameSX, text="AVAILABLE PLUG-IN", font=("Felix Titling", 40))
        self.labelPSelezionabili.pack(pady=10)

        self.listaPlugin = ctk.CTkScrollableFrame(self.frameSX, width=350, height=200, corner_radius=10)
        self.listaPlugin.pack(pady=10)

        self.labelGestisciP = ctk.CTkLabel(self.frameSX, text="MANAGE PLUG-IN", font=("Felix Titling", 40))
        self.labelGestisciP.pack(pady=10)
            
        self.bottoneRimuoviP = ctk.CTkButton(self.frameSX, text="REMOVE PLUG-IN", corner_radius=5, command=self.rimuoviPlugin)
        self.bottoneRimuoviP.pack(pady=10)

        self.bottoneRinominaP = ctk.CTkButton(self.frameSX, text="RENAME PLUG-IN", corner_radius=5)
        self.bottoneRinominaP.pack(pady=10)

        self.labelInfoP = ctk.CTkLabel(self.frameDX, text="TEST ANALYSIS", font=("Felix Titling", 40))
        self.labelInfoP.pack(pady=20)

        self.informazioniTest = ctk.CTkTabview(self.frameDX, width=350, height=400, corner_radius=10)
        self.informazioniTest.pack(pady=10)

        self.testDescription = self.informazioniTest.add("TEST DESCRIPTION")
        ctk.CTkButton(self.testDescription, text="CONFIGURE TEST", command=self.configuraTest).pack(pady=10)
        ctk.CTkButton(self.testDescription, text="START TEST", command=self.iniziaTest).pack(pady=10)
        mostraDescrizioneTest = ctk.CTkLabel(self.testDescription, text="A").pack(pady=10)

        self.testResult = self.informazioniTest.add("TEST RESULT")
        mostraRisultatoTest = ctk.CTkLabel(self.testResult, text="A").pack(pady=10)
        ctk.CTkButton(self.testResult, text="SAVE RESULT").pack(pady=10)

        self.bottoneResLogs = ctk.CTkButton(self.frameDX, text="TEST LOGS", corner_radius=8, command=self.mostraLogs)
        self.bottoneResLogs.pack(pady=10)

    def aggiornaListaPlugin(self):
        for widget in self.listaPlugin.winfo_children():
            widget.destroy()
            plugin_list = self.coreApplicazione.ottieni_lista_plugin()
            if plugin_list is None:  # Se la lista è None, la sostituisci con una lista vuota
                plugin_list = []
            for plugin in plugin_list:
                label = ctk.CTkLabel(self.listaPlugin, text=plugin, cursor="hand2")
                label.pack(pady=5, fill="x")
                label.bind("<Button-1>", lambda e, p=plugin: self.selezionaPlugin(p))

    def selezionaPlugin(self, plugin_name):
        self.plugin_selezionato = plugin_name
        print(f"Plugin selezionato: {plugin_name}")
            # Puoi aggiungere qui la logica per gestire la selezione del plugin

    def caricaPlugin(self):
        if self.coreApplicazione is None:
            messagebox.showerror("Error", "Core dell'applicazione non inizializzato!")
            return
        percorsoPlugin = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if percorsoPlugin:
            try:
                idPlugin = self.coreApplicazione.aggiungi_plugin(percorsoPlugin)
                self.aggiungiPlugin(percorsoPlugin, idPlugin)
                self.aggiornaListaPlugin()
            except Exception as e:
                messagebox.showerror("Error", f"Errore nel caricamento del plug-in: {e}")

    def rimuoviPlugin(self):
        if self.plugin_selezionato is None:
            messagebox.showwarning("Nessun plugin selezionato", "Seleziona un plugin prima di rimuoverlo.")
            return
        try:
            self.coreApplicazione.rimuovi_plugin(self.plugin_selezionato)
            self.aggiornaListaPlugin()
            self.plugin_selezionato = None
        except Exception as e:
            messagebox.showerror("Error", f"Errore nella rimozione del plug-in: {e}")

    def configuraTest(self):
        if self.plugin_selezionato is None:
            messagebox.showwarning("Nessun plugin selezionato", "Seleziona un plugin prima di configurare il test.")
            return
        finestraConfig = ctk.CTkToplevel(self.finestraPrincipale)
        finestraConfig.title(f"Configurazione di: {self.plugin_selezionato}")
        finestraConfig.geometry("400x400")
        finestraConfig.resizable(False, False)
        ctk.CTkLabel(finestraConfig, text="TEST PARAMETERS").pack(pady=10)
        plugin_params = self.coreApplicazione.ottieniListaPlugin()
        for param in plugin_params:
            frameCampoInput = ctk.CTkFrame(master=finestraConfig)
            frameCampoInput.pack(fill="x", pady=5)

            labelNomeCampo = ctk.CTkLabel(master=frameCampoInput, text=f"Campo: {param}")
            labelNomeCampo.pack(side="left", padx=10)

            valoreInseritoInput = ctk.CTkEntry(master=frameCampoInput)
            valoreInseritoInput.pack(side="left", fill="x", expand=True)
    def iniziaTest(self):
        if self.plugin_selezionato is None:
            messagebox.showwarning("Nessun plugin selezionato", "Seleziona un plugin prima di avviare il test.")
            return
        try:
            parametriTest = {} 
            self.coreApplicazione.avvia_test(self.plugin_selezionato, parametriTest)
        except Exception as e:
            messagebox.showerror("Error", f"Errore nell'inizializzazione del test: {e}")

    def aggiungiPlugin(self, name, idPlugin):
        self.plugin_files[name] = {'id': idPlugin}
        self.aggiornaListaPlugin()

    def mostraLogs(self): #!
        try:
            logs = self.coreApplicazione.ottieni_logs_test() #
            messagebox.showinfo("Test Logs", logs)
        except Exception as e:
            messagebox.showerror("Error", f"Errore nel recupero dei log: {e}")



if __name__ == "__main__":
    root = ctk.CTk()
    core = ClientCore()
    app = MainInterfaccia(root, core)
    app.pack(expand=True, fill="both")
    root.mainloop()
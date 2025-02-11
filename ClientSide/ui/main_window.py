import customtkinter as ctk
from tkinter import filedialog, messagebox
from core.core import ClientCore  # Importa il core dell'applicazione

class MainInterfaccia(ctk.CTkFrame):
    def __init__(self, finestraPrincipale, coreApplicazione):
        super().__init__(finestraPrincipale)
        self.finestraPrincipale = finestraPrincipale
        self.coreApplicazione = coreApplicazione
        self.vFilePlugin = {}  # Dizionario per memorizzare i plugin e i loro ID
        self.initUI()

    def initUI(self):
        """
        Inizializza l'interfaccia grafica.
        """
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")

        self.finestraPrincipale.title("PlugInk")
        self.finestraPrincipale.geometry("1000x600")
        self.finestraPrincipale.resizable(False, False)

        # Creazione dei frame sinistro e destro
        self.frameSX = ctk.CTkFrame(self.finestraPrincipale, width=400, height=600)
        self.frameSX.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.frameDX = ctk.CTkFrame(self.finestraPrincipale, width=400, height=600)
        self.frameDX.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.finestraPrincipale.grid_columnconfigure(0, weight=1)
        self.finestraPrincipale.grid_columnconfigure(1, weight=1)
        self.finestraPrincipale.grid_rowconfigure(0, weight=1)

        # FRAME SX
        self.labelCaricaP = ctk.CTkLabel(self.frameSX, text="LOAD PLUG-IN", font=("Felix Titling", 40))
        self.labelCaricaP.pack(pady=10)

        self.bottoneCaricaP = ctk.CTkButton(self.frameSX, text="BROWSE", corner_radius=5, command=self.caricaPlugin)
        self.bottoneCaricaP.pack(pady=10)

        self.labelPSelezionabili = ctk.CTkLabel(self.frameSX, text="AVAILABLE PLUG-IN", font=("Felix Titling", 40))
        self.labelPSelezionabili.pack(pady=10)

        # Usiamo un CTkScrollableFrame per la lista dei plugin
        self.listaPlugin = ctk.CTkScrollableFrame(self.frameSX, width=350, height=200, corner_radius=10)
        self.listaPlugin.pack(pady=10)

        self.labelGestisciP = ctk.CTkLabel(self.frameSX, text="MANAGE PLUG-IN", font=("Felix Titling", 40))
        self.labelGestisciP.pack(pady=10)

        self.bottoneRimuoviP = ctk.CTkButton(self.frameSX, text="REMOVE PLUG-IN", corner_radius=5, command=self.rimuoviPlugin)
        self.bottoneRimuoviP.pack(pady=10)

        self.bottoneRinominaP = ctk.CTkButton(self.frameSX, text="RENAME PLUG-IN", corner_radius=5)
        self.bottoneRinominaP.pack(pady=10)

        # FRAME DX
        self.labelInfoP = ctk.CTkLabel(self.frameDX, text="TEST ANALYSIS", font=("Felix Titling", 40))
        self.labelInfoP.pack(pady=20)

        self.informazioniTest = ctk.CTkTabview(self.frameDX, width=350, height=400, corner_radius=10)
        self.informazioniTest.pack(pady=10)

        self.testDescription = self.informazioniTest.add("TEST DESCRIPTION")
        ctk.CTkLabel(self.testDescription, text="INFO DEL TEST").pack(pady=10)
        ctk.CTkButton(self.testDescription, text="CONFIGURA TEST", command=self.configuraTest).pack(pady=10)
        ctk.CTkButton(self.testDescription, text="START TEST", command=self.iniziaTest).pack(pady=10)

        self.testResult = self.informazioniTest.add("TEST RESULT")
        ctk.CTkLabel(self.testResult, text="TEST OUTPUT").pack(pady=10)
        ctk.CTkButton(self.testResult, text="SALVA RES TEST").pack(pady=10)

        self.bottoneResLogs = ctk.CTkButton(self.frameDX, text="MOSTRA TEST LOGS", corner_radius=8)
        self.bottoneResLogs.pack(pady=10)

    def aggiornaListaPlugin(self):
        """
        Aggiorna la lista dei plugin visualizzata nell'interfaccia.
        """
        for widget in self.listaPlugin.winfo_children():
            widget.destroy()  # Rimuove tutti i widget esistenti
        plugin_list = self.coreApplicazione.ottieni_lista_plugin()
        for plugin in plugin_list:
            ctk.CTkLabel(self.listaPlugin, text=plugin).pack()

    def caricaPlugin(self):
        """
        Carica un plugin selezionato dall'utente.
        """
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
        """
        Rimuove il plugin selezionato.
        """
        try:
            self.coreApplicazione.rimuovi_plugin()
            self.aggiornaListaPlugin()
        except Exception as e:
            messagebox.showerror("Error", f"Errore nella rimozione del plug-in: {e}")

    def configuraTest(self):
        """
        Configura i parametri del test per il plugin selezionato.
        """
        pluginSelezionato = "Plugin1"  # Simula la selezione di un plugin
        if pluginSelezionato:
            finestraConfig = ctk.CTkToplevel(self.finestraPrincipale)
            finestraConfig.title(f"Configurazione di: {pluginSelezionato}")
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
        """
        Avvia il test per il plugin selezionato.
        """
        pluginSelezionato = "Plugin1"  # Simula la selezione di un plugin
        if pluginSelezionato:
            try:
                parametriTest = {}
                self.coreApplicazione.avvia_test("1", parametriTest)  # ID fittizio
            except Exception as e:
                messagebox.showerror("Error", f"Errore nell'inizializzazione del test: {e}")

    def aggiungiPlugin(self, name, idPlugin):
        """
        Aggiunge un plugin alla lista visualizzata e al dizionario.
        """
        ctk.CTkLabel(self.listaPlugin, text=name).pack()
        self.vFilePlugin[name] = {'id': idPlugin}
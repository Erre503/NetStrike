import customtkinter as ctk
from tkinter import filedialog, messagebox
from core.core import ClientCore  # Importa il core dell'applicazione
import os


class MainInterfaccia(ctk.CTkFrame):
    def __init__(self, finestraPrincipale, coreApplicazione):
        super().__init__(finestraPrincipale)
        self.finestraPrincipale = finestraPrincipale
        self.coreApplicazione = coreApplicazione
        self.plugin_files = {}
        self.mode = "p"

        self.plugin_selezionato = None
        self.selected_params = None
        self.log_selezionato = None


    def initUI(self):
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("green")

        self.finestraPrincipale.title("NetStrike")
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


        self.bottoneRinominaP = ctk.CTkButton(self.frameSX, text="RENAME PLUG-IN", corner_radius=5, command=self.modificaPlugin)
        self.bottoneRinominaP.pack(pady=10)


        self.labelView = ctk.CTkLabel(self.frameDX, text="CHANGE VIEW", font=("Felix Titling", 40))
        self.labelView.pack(pady=10)


        self.bottoneUpdate = ctk.CTkButton(self.frameDX, text="UPDATE SCRIPT LIST", corner_radius=8, command=self.aggiornaListaPlugin)
        self.bottoneUpdate.pack(pady=10)
        self.bottoneUpdate.configure(state="disabled")

        self.bottoneView = ctk.CTkButton(self.frameDX, text="VIEW TEST LOGS", corner_radius=8, command=self.cambiaView)
        self.bottoneView.pack(pady=10)


        self.labelInfoP = ctk.CTkLabel(self.frameDX, text="TEST ANALYSIS", font=("Felix Titling", 40))
        self.labelInfoP.pack(pady=10)


        self.labelInfoPluginSelezionato = ctk.CTkLabel(self.frameDX,width=350, text="SELECTED PLUG-IN: None", font=("Arial",20))
        self.labelInfoPluginSelezionato.pack(pady=10)


        self.informazioniTest = ctk.CTkTabview(self.frameDX, width=350, height=200, corner_radius=10)
        self.informazioniTest.pack(pady=10)


        self.testDescription = self.informazioniTest.add("DESCRIPTION")
        self.mostraDescrizioneTest = ctk.CTkLabel(self.testDescription, text="Select a plug-in to view the test details.")
        self.mostraDescrizioneTest.pack(pady=10)


        self.bottoneConfig = ctk.CTkButton(self.frameDX, text="CONFIGURE TEST",corner_radius=8, command=self.configuraTest)
        self.bottoneConfig.pack(pady=10)


        self.bottoneStart = ctk.CTkButton(self.frameDX, text="START TEST",corner_radius=8, command=self.iniziaTest)
        self.bottoneStart.pack(pady=10)

        self.bottoneRoutine = ctk.CTkButton(self.frameDX, text="CREATE ROUTINE TEST",corner_radius=8, command=self.creaRoutine)
        self.bottoneRoutine.pack(pady=10)


        self.aggiornaListaPlugin()


    def aggiornaListaPlugin(self):
        self.svuota_lista()
        self.bottoneUpdate.configure(state="disabled")
        self.coreApplicazione.ottieni_lista_plugin()

    def aggiornaListaTest(self):
        self.svuota_lista()
        self.coreApplicazione.ottieni_lista_test()


    def aggiungi_elemento(self, name, plugin_id):
        button = ctk.CTkButton(self.listaPlugin, text=name, command=lambda name=name: self.selezionaPlugin(name))
        button.pack(pady=5, fill="x")
        self.plugin_files[name] = {'id': plugin_id}


    def svuota_lista(self):
        for widget in self.listaPlugin.winfo_children():
            widget.destroy()


    def mostra_dettagli(self, d):
        if self.mode == "p":
            self.selected_params = d["params"].split(" , ")
        else:
            self.selected_params = ""
        dettagli = ""
        for i in d:
            dettagli += (i+": "+ str(d[i]) + "\n")
        self.mostraDescrizioneTest.configure(text=dettagli)


    def mostra_risultato_test(self, status, log, datetime):
        messagebox.showinfo("Test Result", f"Status: {status}\nLog: {log}\nDateTime: {datetime}")


    def selezionaPlugin(self, name):
        self.plugin_selezionato = self.plugin_files.get(name)['id']
        self.labelInfoPluginSelezionato.configure(text="SELECTED "+("PLUGIN" if self.mode == "p" else "LOG")+f": {name}")
        self.coreApplicazione.ottieni_dettagli(self.plugin_selezionato, 'plugin' if self.mode == "p" else 'test')


    def caricaPlugin(self):
        if self.coreApplicazione is None:
            messagebox.showerror("Error", "Core dell'applicazione non inizializzato!")
            return
        percorsoPlugin = filedialog.askopenfilename(filetypes=[("Python Files", "*.*")])
        if percorsoPlugin:
            try:
                idPlugin = self.coreApplicazione.aggiungi_elemento(percorsoPlugin)
                self.aggiungiPlugin(percorsoPlugin, idPlugin)
                self.aggiornaListaPlugin()
            except Exception as e:
                messagebox.showerror("Error", f"Errore nel caricamento del plug-in: {e}")


    def modificaPlugin(self):
        if self.plugin_selezionato is None:
            messagebox.showwarning("Nessun plugin selezionato", "Seleziona un plugin prima di modificarlo.")
            return

        # Create the edit window
        finestraEdit = ctk.CTkToplevel(self.finestraPrincipale)
        finestraEdit.title(f"RENAME PLUGIN: {self.plugin_selezionato}")
        finestraEdit.geometry("400x800")
        finestraEdit.resizable(False, False)
        finestraEdit.deiconify()
        finestraEdit.update_idletasks()  # Force window initialization

        # Delay grab_set to ensure window is viewable
        finestraEdit.after(100, finestraEdit.grab_set)  # <-- Fix here

        # Widgets
        ctk.CTkLabel(finestraEdit, text="MODIFY TEST NAME:", font=("Felix Titling", 30)).pack(pady=20)
        nuovoNomeEntry = ctk.CTkEntry(finestraEdit, width=300)
        nuovoNomeEntry.pack(pady=10)
        
        ctk.CTkLabel(finestraEdit, text="MODIFY TEST DESCRIPTION:", font=("Felix Titling", 30)).pack(pady=20)
        nuovaDescrizioneEntry = ctk.CTkEntry(finestraEdit, width=300)
        nuovaDescrizioneEntry.pack(pady=10)

        # Define submit function FIRST
        def submitModificaPlugin():
            nomeModificato = nuovoNomeEntry.get()
            descrizioneModificata = nuovaDescrizioneEntry.get()
            try:
                self.coreApplicazione.modifica_plugin(self.plugin_selezionato, nomeModificato, descrizioneModificata)
                finestraEdit.destroy()
                self.aggiornaListaPlugin()
                self.plugin_selezionato = None
                self.selected_params= None
            except Exception as e:
                messagebox.showerror("Errore", f"Errore nella modifica del plug-in: {e}")

        # Create button AFTER defining the submit function
        bottoneSubmit = ctk.CTkButton(
            finestraEdit, 
            text="SUBMIT", 
            corner_radius=5, 
            command=submitModificaPlugin
        )
        bottoneSubmit.pack(pady=20)


   
    def rimuoviPlugin(self):
        if self.plugin_selezionato is None:
            messagebox.showwarning("Nessun plugin selezionato", "Seleziona un plugin prima di rimuoverlo.")
            return
        try:
            self.coreApplicazione.rimuovi_plugin(str(self.plugin_selezionato))
            self.plugin_selezionato = None
            self.selected_params= None
            self.labelInfoPluginSelezionato.configure(text="SELECTED PLUG-IN: None")
        except Exception as e:
            messagebox.showerror("Error", f"Errore nella rimozione del plug-in: {e}")


    def configuraTest(self, edit=True):
        if self.plugin_selezionato is None:
            messagebox.showwarning("Nessun plugin selezionato", "Seleziona un plugin prima di configurare il test.")
            return


        # Create the configuration window
        finestraRoutine = ctk.CTkToplevel(self.finestraPrincipale)
        finestraRoutine.title("CREAZIONE ROUTINE")
        finestraRoutine.geometry("400x700")
        finestraRoutine.resizable(False, False)

        # Ensure the window is visible and ready
        finestraRoutine.deiconify()
        finestraRoutine.update_idletasks()  # Force window to process pending events

        # Delay the grab_set to ensure the window is fully viewable
        finestraRoutine.after(100, finestraRoutine.grab_set)
        if not edit:
            # Frequency
            ctk.CTkLabel(finestraRoutine, text="FREQUENCY").pack(pady=10)
            frequencyFrame = ctk.CTkFrame(master=finestraRoutine)
            frequencyFrame.pack(fill="x", pady=1)
            frequency = ctk.CTkEntry(master=frequencyFrame)
            frequency.pack(side="left", fill="x", expand=True)

            # First dt
            ctk.CTkLabel(finestraRoutine, text="FIRST DATETIME").pack(pady=10)
            first_dtFrame = ctk.CTkFrame(master=finestraRoutine)
            first_dtFrame.pack(fill="x", pady=1)
            first_dt = ctk.CTkEntry(master=first_dtFrame)
            first_dt.pack(side="left", fill="x", expand=True)

        # Params
        paramsEntry = []
        if self.selected_params[0]!= '':
            ctk.CTkLabel(finestraRoutine, text="PARAMETERS").pack(pady=10)
            i=0
            for param in self.selected_params:
                frameCampoInput = ctk.CTkFrame(master=finestraRoutine)
                frameCampoInput.pack(fill="x", pady=5)
                labelNomeCampo = ctk.CTkLabel(master=frameCampoInput, text=f"Campo: {param}")
                labelNomeCampo.pack(side="left", padx=10)
                paramsEntry.append(ctk.CTkEntry(master=frameCampoInput))
                paramsEntry[i].pack(side="left", fill="x", expand=True)
                i+=1

        def submit():
            params = {}
            i = 0
            for param in paramsEntry:
                params[self.selected_params[i]] = param.get()
                i+=1
            if edit:
                self.coreApplicazione.avvia_test(self.plugin_selezionato, params)
            else:
                self.coreApplicazione.crea_routine(self.plugin_selezionato, params, int(frequency.get()), first_dt.get())
            finestraRoutine.destroy()

        submitButton =  ctk.CTkButton(master=finestraRoutine, text="SUBMIT", corner_radius=5, command=submit)
        submitButton.pack(pady=50)


        


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

    def creaRoutine(self):
        self.configuraTest(False)

    def notifica(self):
        print("Stato bottone: ", self.bottoneUpdate.cget("state"))
        if(self.bottoneUpdate.cget("state") == "disabled"):
            self.bottoneUpdate.configure(state="normal")
        

    def cambiaView(self):
        if self.mode == "p":
            self.mode = "t"
            self.coreApplicazione.stop_polling()
            self.labelCaricaP.pack_forget()
            self.bottoneCaricaP.pack_forget()


            self.labelInfoP.configure(text="LOG DESCRIPTION")
            self.labelInfoPluginSelezionato.configure(text="SELECTED LOG: None")




            self.labelPSelezionabili.configure(text="AVAILABLE LOGS")


            self.labelGestisciP.configure(text="MANAGE LOGS")


            self.bottoneRinominaP.configure(text="EDIT LOG")
            self.bottoneUpdate.pack_forget()
            self.bottoneView.configure(text="VIEW PLUG-INs")
            self.bottoneRimuoviP.pack_forget()
            self.bottoneConfig.pack_forget()
            self.bottoneStart.pack_forget()

            self.aggiornaListaTest()
           
        else:
            self.mode = "p"
            self.coreApplicazione.start_polling()
            self.labelCaricaP.pack(pady=10)
            self.bottoneCaricaP.pack(pady=10)


            self.labelInfoP.pack_forget()
            self.labelInfoP.configure(text="TEST ANALYSYS")
            self.labelInfoPluginSelezionato.pack_forget()
            self.labelInfoPluginSelezionato.configure(text="SELECTED PLUG-IN: None")
            self.labelInfoP.pack(pady=10)
            self.labelInfoPluginSelezionato.pack(pady=10)


            self.labelPSelezionabili.pack_forget()
            self.labelPSelezionabili.configure(text="AVAILABLE PLUG-IN")
            self.labelPSelezionabili.pack(pady=10)
            self.listaPlugin.pack_forget()
            self.listaPlugin.pack(pady=10)


            self.labelGestisciP.pack_forget()
            self.labelGestisciP.configure(text="MANAGE PLUG-IN")
            self.labelGestisciP.pack(pady=10)


            self.bottoneRinominaP.pack_forget()
            self.bottoneRinominaP.configure(text="EDIT PLUG-IN")
            self.bottoneRinominaP.pack(pady=10)


            self.bottoneRimuoviP.pack(pady=10)
            self.bottoneView.configure(text="VIEW TEST LOGS")
            self.bottoneUpdate.pack(before=self.bottoneView)
            self.bottoneUpdate.configure(state="disabled")
            self.informazioniTest.pack(pady=10)
            self.bottoneConfig.pack(pady=10)
            self.bottoneStart.pack(pady=10)

            self.aggiornaListaPlugin()
        
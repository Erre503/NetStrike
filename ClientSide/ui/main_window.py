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
        
        # Store original positions for elements
        self.original_positions = {}
        
        # Variables for filtering
        self.filtered_items = {}
        self.filter_active = False
        self.search_var = None

    def set_icon_for_window(self, window):
        """Set icon for any window"""
        try:
            icona = os.path.join(os.path.dirname(__file__), 'er.ico')
            if os.path.exists(icona):
                window.wm_iconbitmap(icona)
        except:
            pass  # Ignore if icon file doesn't exist or can't be set

    def initUI(self):
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("green")

        self.finestraPrincipale.title("NetStrike")
        self.finestraPrincipale.geometry("1000x650")
        self.finestraPrincipale.resizable(False, False)
        
        # Set icon for main window
        self.set_icon_for_window(self.finestraPrincipale)

        # Create main frames
        self.frameSX = ctk.CTkFrame(self.finestraPrincipale, width=400, height=600)
        self.frameSX.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.frameDX = ctk.CTkFrame(self.finestraPrincipale, width=400, height=600)
        self.frameDX.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.finestraPrincipale.grid_columnconfigure(0, weight=1)
        self.finestraPrincipale.grid_columnconfigure(1, weight=1)
        self.finestraPrincipale.grid_rowconfigure(0, weight=1)

        # LEFT FRAME - PLUGIN MANAGEMENT
        self.labelCaricaP = ctk.CTkLabel(self.frameSX, text="LOAD PLUG-IN", font=("Felix Titling", 24))
        self.labelCaricaP.pack(pady=(10, 5))

        self.bottoneCaricaP = ctk.CTkButton(self.frameSX, text="BROWSE", corner_radius=5, command=self.caricaPlugin)
        self.bottoneCaricaP.pack(pady=5)

        self.labelPSelezionabili = ctk.CTkLabel(self.frameSX, text="AVAILABLE PLUG-IN", font=("Felix Titling", 24))
        self.labelPSelezionabili.pack(pady=(15, 5))

        # Search frame
        self.search_frame = ctk.CTkFrame(self.frameSX)
        self.search_frame.pack(pady=5, fill="x", padx=10)
        
        self.search_var = ctk.StringVar()
        self.search_var.trace('w', self.filter_items)
        
        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Search...", textvariable=self.search_var)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(5, 2))
        
        self.clear_filter_btn = ctk.CTkButton(self.search_frame, text="Clear", width=60, command=self.clear_filter)
        self.clear_filter_btn.pack(side="right", padx=(2, 5))

        self.listaPlugin = ctk.CTkScrollableFrame(self.frameSX, width=350, height=180, corner_radius=10)
        self.listaPlugin.pack(pady=5, fill="both", expand=True)

        self.labelGestisciP = ctk.CTkLabel(self.frameSX, text="MANAGE PLUG-IN", font=("Felix Titling", 24))
        self.labelGestisciP.pack(pady=(10, 5))
                   
        self.bottoneRimuoviP = ctk.CTkButton(self.frameSX, text="REMOVE PLUG-IN", corner_radius=5, command=self.rimuoviPlugin)
        self.bottoneRimuoviP.pack(pady=3)

        self.bottoneRinominaP = ctk.CTkButton(self.frameSX, text="RENAME PLUG-IN", corner_radius=5, command=self.modificaPlugin)
        self.bottoneRinominaP.pack(pady=3)

        # RIGHT FRAME - TEST MANAGEMENT AND VIEW
        self.labelView = ctk.CTkLabel(self.frameDX, text="CHANGE VIEW", font=("Felix Titling", 24))
        self.labelView.pack(pady=(10, 5))

        self.bottoneUpdate = ctk.CTkButton(self.frameDX, text="UPDATE SCRIPT LIST", corner_radius=8, command=self.aggiornaListaPlugin)
        self.bottoneUpdate.pack(pady=3)
        self.bottoneUpdate.configure(state="disabled")

        self.bottoneView = ctk.CTkButton(self.frameDX, text="VIEW TEST LOGS", corner_radius=8, command=self.cambiaView)
        self.bottoneView.pack(pady=3)

        self.labelInfoP = ctk.CTkLabel(self.frameDX, text="TEST ANALYSIS", font=("Felix Titling", 24))
        self.labelInfoP.pack(pady=(15, 5))

        self.labelInfoPluginSelezionato = ctk.CTkLabel(self.frameDX, width=350, text="SELECTED PLUG-IN: None", font=("Arial", 16))
        self.labelInfoPluginSelezionato.pack(pady=5)

        self.informazioniTest = ctk.CTkTabview(self.frameDX, width=350, height=150, corner_radius=10)
        self.informazioniTest.pack(pady=5)

        self.testDescription = self.informazioniTest.add("DESCRIPTION")
        self.mostraDescrizioneTest = ctk.CTkLabel(self.testDescription, text="Select a plug-in to view the test details.", wraplength=320)
        self.mostraDescrizioneTest.pack(pady=10)

        # Action buttons
        self.bottoneConfig = ctk.CTkButton(self.frameDX, text="CONFIGURE TEST", corner_radius=8, command=self.configuraTest)
        self.bottoneConfig.pack(pady=3)

        self.bottoneStart = ctk.CTkButton(self.frameDX, text="START TEST", corner_radius=8, command=self.iniziaTest)
        self.bottoneStart.pack(pady=3)

        self.bottoneRoutine = ctk.CTkButton(self.frameDX, text="CREATE ROUTINE TEST", corner_radius=8, command=self.creaRoutine)
        self.bottoneRoutine.pack(pady=3)

        # Store original positions
        self.store_original_positions()
        
        self.aggiornaListaPlugin()

    def store_original_positions(self):
        """Store original positions of widgets for view switching"""
        self.original_positions = {
            'labelCaricaP': {'visible': True, 'pack_info': self.labelCaricaP.pack_info()},
            'bottoneCaricaP': {'visible': True, 'pack_info': self.bottoneCaricaP.pack_info()},
            'labelPSelezionabili': {'visible': True, 'pack_info': self.labelPSelezionabili.pack_info()},
            'labelGestisciP': {'visible': True, 'pack_info': self.labelGestisciP.pack_info()},
            'bottoneRimuoviP': {'visible': True, 'pack_info': self.bottoneRimuoviP.pack_info()},
            'bottoneRinominaP': {'visible': True, 'pack_info': self.bottoneRinominaP.pack_info()},
            'bottoneUpdate': {'visible': True, 'pack_info': self.bottoneUpdate.pack_info()},
            'bottoneConfig': {'visible': True, 'pack_info': self.bottoneConfig.pack_info()},
            'bottoneStart': {'visible': True, 'pack_info': self.bottoneStart.pack_info()},
            'bottoneRoutine': {'visible': True, 'pack_info': self.bottoneRoutine.pack_info()},
        }

    def filter_items(self, *args):
        """Filter items based on search text"""
        search_text = self.search_var.get().lower().strip()
        
        if not search_text:
            self.clear_filter()
            return
            
        self.filter_active = True
        
        # Clear current list
        for widget in self.listaPlugin.winfo_children():
            widget.destroy()
            
        # Show only matching items
        for name, data in self.plugin_files.items():
            if search_text in name.lower():
                button = ctk.CTkButton(self.listaPlugin, text=name, command=lambda name=name: self.selezionaPlugin(name))
                button.pack(pady=5, fill="x")

    def clear_filter(self):
        """Clear the filter and show all items"""
        self.search_var.set("")
        self.filter_active = False
        self.refresh_item_list()

    def refresh_item_list(self):
        """Refresh the item list"""
        # Clear current list
        for widget in self.listaPlugin.winfo_children():
            widget.destroy()
            
        # Restore all items
        for name, data in self.plugin_files.items():
            button = ctk.CTkButton(self.listaPlugin, text=name, command=lambda name=name: self.selezionaPlugin(name))
            button.pack(pady=5, fill="x")

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
        self.plugin_files.clear()

    def mostra_dettagli(self, d):
        if self.mode == "p":
            self.selected_params = d["params"].split(" , ") if "params" in d and d["params"] else []
        else:
            self.selected_params = ""
        dettagli = ""
        for i in d:
            dettagli += (i + ": " + str(d[i]) + "\n")
        self.mostraDescrizioneTest.configure(text=dettagli)

    def mostra_risultato_test(self, status, log, datetime):
        messagebox.showinfo("Test Result", f"Status: {status}\nLog: {log}\nDateTime: {datetime}")

    def selezionaPlugin(self, name):
        if name in self.plugin_files:
            self.plugin_selezionato = self.plugin_files.get(name)['id']
            self.labelInfoPluginSelezionato.configure(text="SELECTED " + ("PLUGIN" if self.mode == "p" else "LOG") + f": {name}")
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

        # Create the edit window with better proportions
        finestraEdit = ctk.CTkToplevel(self.finestraPrincipale)
        finestraEdit.title(f"RENAME PLUGIN: {self.plugin_selezionato}")
        finestraEdit.geometry("500x400")
        finestraEdit.resizable(False, False)
        
        # Set icon and keep on top
        self.set_icon_for_window(finestraEdit)
        finestraEdit.attributes('-topmost', True)
        finestraEdit.transient(self.finestraPrincipale)
        
        finestraEdit.deiconify()
        finestraEdit.update_idletasks()
        finestraEdit.after(100, finestraEdit.grab_set)

        # Main frame with padding
        main_frame = ctk.CTkFrame(finestraEdit)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_label = ctk.CTkLabel(main_frame, text="MODIFY PLUGIN", font=("Felix Titling", 24))
        title_label.pack(pady=(0, 20))

        # Name section
        name_frame = ctk.CTkFrame(main_frame)
        name_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(name_frame, text="NEW NAME:", font=("Arial", 14, "bold")).pack(pady=(10, 5))
        nuovoNomeEntry = ctk.CTkEntry(name_frame, width=400, height=35)
        nuovoNomeEntry.pack(pady=(0, 10), padx=10)

        # Description section
        desc_frame = ctk.CTkFrame(main_frame)
        desc_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(desc_frame, text="NEW DESCRIPTION:", font=("Arial", 14, "bold")).pack(pady=(10, 5))
        nuovaDescrizioneEntry = ctk.CTkEntry(desc_frame, width=400, height=35)
        nuovaDescrizioneEntry.pack(pady=(0, 10), padx=10)

        # Buttons frame
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=20)

        def submitModificaPlugin():
            nomeModificato = nuovoNomeEntry.get()
            descrizioneModificata = nuovaDescrizioneEntry.get()
            try:
                self.coreApplicazione.modifica_plugin(self.plugin_selezionato, nomeModificato, descrizioneModificata)
                finestraEdit.destroy()
                # Fix: Update the correct list based on current mode
                if self.mode == "p":
                    self.aggiornaListaPlugin()
                else:
                    self.aggiornaListaTest()
                self.plugin_selezionato = None
                self.selected_params = None
            except Exception as e:
                messagebox.showerror("Errore", f"Errore nella modifica del plug-in: {e}")

        def annulla():
            finestraEdit.destroy()

        # Buttons
        bottoneSubmit = ctk.CTkButton(button_frame, text="SUBMIT", corner_radius=5, command=submitModificaPlugin, width=120)
        bottoneSubmit.pack(side="left", padx=(10, 5), pady=10)
        
        bottoneAnnulla = ctk.CTkButton(button_frame, text="CANCEL", corner_radius=5, command=annulla, width=120)
        bottoneAnnulla.pack(side="right", padx=(5, 10), pady=10)

    def rimuoviPlugin(self):
        if self.plugin_selezionato is None:
            messagebox.showwarning("Nessun plugin selezionato", "Seleziona un plugin prima di rimuoverlo.")
            return
        try:
            self.coreApplicazione.rimuovi_plugin(str(self.plugin_selezionato))
            self.plugin_selezionato = None
            self.selected_params = None
            self.labelInfoPluginSelezionato.configure(text="SELECTED PLUG-IN: None")
            # Fix: Update the correct list based on current mode
            if self.mode == "p":
                self.aggiornaListaPlugin()
            else:
                self.aggiornaListaTest()
        except Exception as e:
            messagebox.showerror("Error", f"Errore nella rimozione del plug-in: {e}")

    def configuraTest(self, edit=True):
        if self.plugin_selezionato is None:
            messagebox.showwarning("Nessun plugin selezionato", "Seleziona un plugin prima di configurare il test.")
            return

        # Create the configuration window with better proportions
        finestraRoutine = ctk.CTkToplevel(self.finestraPrincipale)
        finestraRoutine.title("CONFIGURAZIONE TEST" if edit else "CREAZIONE ROUTINE")
        
        # Calculate height based on parameters
        base_height = 200
        param_height = len(self.selected_params) * 60 if self.selected_params and self.selected_params[0] != '' else 0
        routine_height = 120 if not edit else 0
        total_height = min(base_height + param_height + routine_height, 700)
        
        finestraRoutine.geometry(f"600x{total_height}")
        finestraRoutine.resizable(False, False)

        # Set icon and keep on top
        self.set_icon_for_window(finestraRoutine)
        finestraRoutine.attributes('-topmost', True)
        finestraRoutine.transient(self.finestraPrincipale)
        
        finestraRoutine.deiconify()
        finestraRoutine.update_idletasks()
        finestraRoutine.after(100, finestraRoutine.grab_set)

        # Main scrollable frame
        main_frame = ctk.CTkScrollableFrame(finestraRoutine)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_text = "CONFIGURAZIONE TEST" if edit else "CREAZIONE ROUTINE"
        title_label = ctk.CTkLabel(main_frame, text=title_text, font=("Felix Titling", 20))
        title_label.pack(pady=(0, 20))

        frequency = None
        first_dt = None

        if not edit:
            # Frequency section
            freq_frame = ctk.CTkFrame(main_frame)
            freq_frame.pack(fill="x", pady=10)
            
            ctk.CTkLabel(freq_frame, text="FREQUENZA (secondi):", font=("Arial", 14, "bold")).pack(pady=(10, 5))
            frequency = ctk.CTkEntry(freq_frame, width=500, height=35)
            frequency.pack(pady=(0, 10), padx=10)

            # First datetime section
            dt_frame = ctk.CTkFrame(main_frame)
            dt_frame.pack(fill="x", pady=10)
            
            ctk.CTkLabel(dt_frame, text="PRIMO DATETIME (YYYY-MM-DD HH:MM:SS):", font=("Arial", 14, "bold")).pack(pady=(10, 5))
            first_dt = ctk.CTkEntry(dt_frame, width=500, height=35)
            first_dt.pack(pady=(0, 10), padx=10)

        # Parameters section
        paramsEntry = []
        if self.selected_params and self.selected_params[0] != '':
            param_frame = ctk.CTkFrame(main_frame)
            param_frame.pack(fill="x", pady=10)
            
            ctk.CTkLabel(param_frame, text="PARAMETRI:", font=("Arial", 14, "bold")).pack(pady=(10, 5))
            
            for i, param in enumerate(self.selected_params):
                field_frame = ctk.CTkFrame(param_frame)
                field_frame.pack(fill="x", pady=5, padx=10)
                
                labelNomeCampo = ctk.CTkLabel(field_frame, text=f"{param}:", font=("Arial", 12))
                labelNomeCampo.pack(side="left", padx=(10, 5))
                
                entry = ctk.CTkEntry(field_frame, height=30)
                entry.pack(side="right", fill="x", expand=True, padx=(5, 10))
                paramsEntry.append(entry)

        # Buttons section
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=20)

        def submit():
            try:
                params = {}
                for i, param_entry in enumerate(paramsEntry):
                    if i < len(self.selected_params):
                        params[self.selected_params[i]] = param_entry.get()
                
                if edit:
                    self.coreApplicazione.avvia_test(self.plugin_selezionato, params)
                else:
                    freq_val = int(frequency.get()) if frequency and frequency.get() else 60
                    dt_val = first_dt.get() if first_dt else ""
                    self.coreApplicazione.crea_routine(self.plugin_selezionato, params, freq_val, dt_val)
                
                finestraRoutine.destroy()
                messagebox.showinfo("Successo", "Operazione completata con successo!")
            except Exception as e:
                messagebox.showerror("Errore", f"Errore durante l'operazione: {e}")

        def annulla():
            finestraRoutine.destroy()

        submitButton = ctk.CTkButton(button_frame, text="SUBMIT", corner_radius=5, command=submit, width=120)
        submitButton.pack(side="left", padx=(10, 5), pady=10)
        
        cancelButton = ctk.CTkButton(button_frame, text="CANCEL", corner_radius=5, command=annulla, width=120)
        cancelButton.pack(side="right", padx=(5, 10), pady=10)

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
        if self.bottoneUpdate.cget("state") == "disabled":
            self.bottoneUpdate.configure(state="normal")

    def cambiaView(self):
        if self.mode == "p":
            # Switch to test/log view
            self.mode = "t"
            self.coreApplicazione.stop_polling()
            
            # Hide plugin-specific elements
            self.labelCaricaP.pack_forget()
            self.bottoneCaricaP.pack_forget()
            self.bottoneRimuoviP.pack_forget()
            self.bottoneUpdate.pack_forget()
            self.bottoneConfig.pack_forget()
            self.bottoneStart.pack_forget()
            self.bottoneRoutine.pack_forget()
            
            # Update text labels
            self.labelInfoP.configure(text="LOG DESCRIPTION")
            self.labelInfoPluginSelezionato.configure(text="SELECTED LOG: None")
            self.labelPSelezionabili.configure(text="AVAILABLE LOGS")
            self.labelGestisciP.configure(text="MANAGE LOGS")
            self.bottoneRinominaP.configure(text="EDIT LOG")
            self.bottoneView.configure(text="VIEW PLUG-INS")
            
            # Update search placeholder
            self.search_entry.configure(placeholder_text="Search logs...")
            
            self.aggiornaListaTest()
           
        else:
            # Switch back to plugin view
            self.mode = "p"
            self.coreApplicazione.start_polling()
            
            # Restore all elements with original positions
            self.labelCaricaP.pack(pady=(10, 5))
            self.bottoneCaricaP.pack(pady=5)
            self.bottoneRimuoviP.pack(pady=3)
            self.bottoneUpdate.pack(before=self.bottoneView, pady=3)
            self.bottoneUpdate.configure(state="disabled")
            self.bottoneConfig.pack(pady=3)
            self.bottoneStart.pack(pady=3)
            self.bottoneRoutine.pack(pady=3)
            
            # Restore text labels
            self.labelInfoP.configure(text="TEST ANALYSIS")
            self.labelInfoPluginSelezionato.configure(text="SELECTED PLUG-IN: None")
            self.labelPSelezionabili.configure(text="AVAILABLE PLUG-IN")
            self.labelGestisciP.configure(text="MANAGE PLUG-IN")
            self.bottoneRinominaP.configure(text="RENAME PLUG-IN")
            self.bottoneView.configure(text="VIEW TEST LOGS")
            
            # Update search placeholder
            self.search_entry.configure(placeholder_text="Search plugins...")
            
            self.aggiornaListaPlugin()
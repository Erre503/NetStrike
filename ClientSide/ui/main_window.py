import customtkinter as ctk  # Import the customtkinter library for creating custom GUI elements
from tkinter import filedialog, messagebox  # Import file dialog and message box for user interactions
from core.core import ClientCore  # Import the core application functionality
import os  # Import the os module for interacting with the operating system
import json

class MainInterfaccia(ctk.CTkFrame):
    """
    Main interface class for the application, inheriting from CTkFrame.

    This class manages the user interface for loading, managing, and executing plugins,
    as well as viewing test logs and configuring tests.
    """

    def __init__(self, finestraPrincipale, coreApplicazione):
        """
        Initializes the MainInterfaccia class.

        Args:
            finestraPrincipale (CTk): The main application window.
            coreApplicazione (ClientCore): The core application instance for managing client-server interactions.
        """
        super().__init__(finestraPrincipale)  # Initialize the parent class
        self.finestraPrincipale = finestraPrincipale  # Store the main window reference
        self.coreApplicazione = coreApplicazione  # Store the core application reference
        self.plugin_files = {}  # Dictionary to store loaded plugin files
        self.mode = "p"  # Current mode (plugin or test log)

        self.plugin_selezionato = None  # Currently selected plugin
        self.selected_params = None  # Parameters of the selected plugin
        self.log_selezionato = None  # Currently selected log

    def initUI(self):
        """
        Initializes the user interface components of the main window.

        This method sets up the layout, appearance, and widgets for the main interface.
        """
        ctk.set_appearance_mode("Dark")  # Set the appearance mode to dark
        ctk.set_default_color_theme("green")  # Set the default color theme to green

        self.finestraPrincipale.title("NetStrike")  # Set the window title
        self.finestraPrincipale.geometry("1000x650")  # Set the window size
        self.finestraPrincipale.resizable(False, False)  # Disable window resizing

        # Create left and right frames for the interface
        self.frameSX = ctk.CTkFrame(self.finestraPrincipale, width=400, height=600)
        self.frameSX.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.frameDX = ctk.CTkFrame(self.finestraPrincipale, width=400, height=600)
        self.frameDX.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Configure grid layout
        self.finestraPrincipale.grid_columnconfigure(0, weight=1)
        self.finestraPrincipale.grid_columnconfigure(1, weight=1)
        self.finestraPrincipale.grid_rowconfigure(0, weight=1)

        # Load Plugin section
        self.labelCaricaP = ctk.CTkLabel(self.frameSX, text="LOAD PLUG-IN", font=("Felix Titling", 40))
        self.labelCaricaP.pack(pady=10)

        self.bottoneCaricaP = ctk.CTkButton(self.frameSX, text="BROWSE", corner_radius=5, command=self.caricaPlugin)
        self.bottoneCaricaP.pack(pady=10)

        # Available Plugins section
        self.labelPSelezionabili = ctk.CTkLabel(self.frameSX, text="AVAILABLE PLUG-IN", font=("Felix Titling", 40))
        self.labelPSelezionabili.pack(pady=10)

        self.listaPlugin = ctk.CTkScrollableFrame(self.frameSX, width=350, height=200, corner_radius=10)
        self.listaPlugin.pack(pady=10)

        # Manage Plugin section
        self.labelGestisciP = ctk.CTkLabel(self.frameSX, text="MANAGE PLUG-IN", font=("Felix Titling", 40))
        self.labelGestisciP.pack(pady=10)

        self.bottoneRimuoviP = ctk.CTkButton(self.frameSX, text="REMOVE PLUG-IN", corner_radius=5, command=self.rimuoviPlugin)
        self.bottoneRimuoviP.pack(pady=10)

        self.bottoneRinominaP = ctk.CTkButton(self.frameSX, text="RENAME PLUG-IN", corner_radius=5, command=self.modificaPlugin)
        self.bottoneRinominaP.pack(pady=10)

        # Change View section
        self.labelView = ctk.CTkLabel(self.frameDX, text="CHANGE VIEW", font=("Felix Titling", 40))
        self.labelView.pack(pady=10)

        self.bottoneUpdate = ctk.CTkButton(self.frameDX, text="UPDATE SCRIPT LIST", corner_radius=8, command=self.aggiornaListaPlugin)
        self.bottoneUpdate.pack(pady=10)
        self.bottoneUpdate.configure(state="disabled")  # Initially disable the update button

        self.bottoneView = ctk.CTkButton(self.frameDX, text="VIEW TEST LOGS", corner_radius=8, command=self.cambiaView)
        self.bottoneView.pack(pady=10)

        # Test Analysis section
        self.labelInfoP = ctk.CTkLabel(self.frameDX, text="TEST ANALYSIS", font=("Felix Titling", 40))
        self.labelInfoP.pack(pady=10)

        self.labelInfoPluginSelezionato = ctk.CTkLabel(self.frameDX, width=350, text="SELECTED PLUG-IN: None", font=("Arial", 20))
        self.labelInfoPluginSelezionato.pack(pady=10)

        self.informazioniTest = ctk.CTkTabview(self.frameDX, width=350, height=200, corner_radius=10)
        self.informazioniTest.pack(pady=10)

        self.testDescription = self.informazioniTest.add("DESCRIPTION")  # Add a tab for test description
        self.mostraDescrizioneTest = ctk.CTkLabel(self.testDescription, text="Select a plug-in to view the test details.")
        self.mostraDescrizioneTest.pack(pady=10)

        # Configure Test section
        self.bottoneConfig = ctk.CTkButton(self.frameDX, text="CONFIGURE TEST", corner_radius=8, command=self.configuraTest)
        self.bottoneConfig.pack(pady=10)

        self.bottoneStart = ctk.CTkButton(self.frameDX, text="START TEST", corner_radius=8, command=self.iniziaTest)
        self.bottoneStart.pack(pady=10)

        self.bottoneRoutine = ctk.CTkButton(self.frameDX, text="CREATE ROUTINE TEST", corner_radius=8, command=self.creaRoutine)
        self.bottoneRoutine.pack(pady=10)

        self.aggiornaListaPlugin()  # Update the plugin list on initialization

    def aggiornaListaPlugin(self):
        """
        Updates the list of available plugins by clearing the current list
        and fetching the latest plugin data from the core application.
        """
        self.svuota_lista()  # Clear the current list of plugins
        self.bottoneUpdate.configure(state="disabled")  # Disable the update button
        self.coreApplicazione.ottieni_lista_plugin()  # Fetch the latest plugin list

    def aggiornaListaTest(self):
        """
        Updates the list of available test logs by clearing the current list
        and fetching the latest test data from the core application.
        """
        self.svuota_lista()  # Clear the current list of tests
        self.coreApplicazione.ottieni_lista_test()  # Fetch the latest test list

    def aggiungi_elemento(self, name, plugin_id):
        """
        Adds a new plugin button to the list of available plugins.

        Args:
            name (str): The name of the plugin.
            plugin_id (str): The ID of the plugin.
        """
        button = ctk.CTkButton(self.listaPlugin, text=name, command=lambda name=name: self.selezionaPlugin(name))
        button.pack(pady=5, fill="x")  # Pack the button into the scrollable frame
        self.plugin_files[name] = {'id': plugin_id}  # Store the plugin ID

    def svuota_lista(self):
        """
        Clears all widgets from the list of available plugins.
        """
        for widget in self.listaPlugin.winfo_children():
            widget.destroy()  # Destroy each widget in the list

    def mostra_dettagli(self, d):
        """
        Displays the details of the selected plugin.

        Args:
            d (dict): A dictionary containing the details of the selected plugin.
        """
        if self.mode == "p":
            self.selected_params = d["params"].split(", ")  # Split parameters into a list
        else:
            self.selected_params = ""
        dettagli = ""
        for i in d:
            dettagli += (i + ": " + str(d[i]) + "\n")  # Format details for display
        self.mostraDescrizioneTest.configure(text=dettagli)  # Update the description label

    def mostra_risultato_test(self, status, log, datetime):
        """
        Displays the result of a test in a message box.

        Args:
            status (str): The status of the test.
            log (str): The log output of the test.
            datetime (str): The date and time of the test execution.
        """
        messagebox.showinfo("Test Result", f"Status: {status}\nLog: {log}\nDateTime: {datetime}")

    def show_error(self, msg):
        """
        Displays the error in a message box.

        Args:
            msg (str): The error message.
        """
        try:
            # Check if the message starts with "Error" and contains JSON
            if msg.startswith("Error") and ':' in msg:
                # Split the message to get the JSON part
                json_part = msg.split(':', 1)[1].strip()
                error_data = json.loads(json_part)  # Parse the JSON
                error_message = error_data.get("error", "An unknown error occurred.")
                error_code = msg.split(' ')[1]  # Extract the error code
                formatted_message = f"Error Code: {error_code}\nError Message: {error_message}"
            else:
                formatted_message = msg  # Fallback to the original message if parsing fails
        except json.JSONDecodeError:
            formatted_message = "An unexpected error occurred. Please try again."
        # Display the formatted error message
        messagebox.showerror("Error", formatted_message)

    def selezionaPlugin(self, name):
        """
        Selects a plugin from the list and fetches its details.

        Args:
            name (str): The name of the selected plugin.
        """
        self.plugin_selezionato = self.plugin_files.get(name)['id']  # Get the ID of the selected plugin
        self.labelInfoPluginSelezionato.configure(text="SELECTED " + ("PLUGIN" if self.mode == "p" else "LOG") + f": {name}")
        self.coreApplicazione.ottieni_dettagli(self.plugin_selezionato, 'plugin' if self.mode == "p" else 'test')  # Fetch details

    def caricaPlugin(self):
        """
        Opens a file dialog to load a plugin and adds it to the application.
        """
        if self.coreApplicazione is None:
            messagebox.showerror("Error", "Core dell'applicazione non inizializzato!")  # Error if core is not initialized
            return
        percorsoPlugin = filedialog.askopenfilename(filetypes=[("Python Files", "*.*")])  # Open file dialog
        if percorsoPlugin:
            try:
                idPlugin = self.coreApplicazione.aggiungi_elemento(percorsoPlugin)  # Add the plugin to the core application
                self.aggiungiPlugin(percorsoPlugin, idPlugin)  # Add the plugin to the UI
                self.aggiornaListaPlugin()  # Update the plugin list
            except Exception as e:
                messagebox.showerror("Error", f"Errore nel caricamento del plug-in: {e}")  # Show error message

    def modificaPlugin(self):
        """
        Opens a window to modify the selected plugin's name and description.
        """
        if self.plugin_selezionato is None:
            messagebox.showwarning("Nessun plugin selezionato", "Seleziona un plugin prima di modificarlo.")  # Warning if no plugin is selected
            return

        # Create the edit window
        finestraEdit = ctk.CTkToplevel(self.finestraPrincipale)  # Create a new top-level window
        finestraEdit.title(f"RENAME PLUGIN: {self.plugin_selezionato}")  # Set the window title
        finestraEdit.geometry("400x800")  # Set the window size
        finestraEdit.resizable(False, False)  # Disable resizing
        finestraEdit.deiconify()  # Show the window
        finestraEdit.update_idletasks()  # Force window initialization

        # Delay grab_set to ensure window is viewable
        finestraEdit.after(100, finestraEdit.grab_set)  # Ensure the window is focused

        # Widgets for renaming the plugin
        ctk.CTkLabel(finestraEdit, text="MODIFY TEST NAME:", font=("Felix Titling", 30)).pack(pady=20)
        nuovoNomeEntry = ctk.CTkEntry(finestraEdit, width=300)  # Entry for new name
        nuovoNomeEntry.pack(pady=10)

        ctk.CTkLabel(finestraEdit, text="MODIFY TEST DESCRIPTION:", font=("Felix Titling", 30)).pack(pady=20)
        nuovaDescrizioneEntry = ctk.CTkEntry(finestraEdit, width=300)  # Entry for new description
        nuovaDescrizioneEntry.pack(pady=10)

        # Define submit function for renaming the plugin
        def submitModificaPlugin():
            nomeModificato = nuovoNomeEntry.get()  # Get the new name
            descrizioneModificata = nuovaDescrizioneEntry.get()  # Get the new description
            try:
                self.coreApplicazione.modifica_plugin(self.plugin_selezionato, nomeModificato, descrizioneModificata)  # Modify the plugin
                finestraEdit.destroy()  # Close the edit window
                self.aggiornaListaPlugin()  # Update the plugin list
                self.plugin_selezionato = None  # Reset selected plugin
                self.selected_params = None  # Reset selected parameters
            except Exception as e:
                messagebox.showerror("Errore", f"Errore nella modifica del plug-in: {e}")  # Show error message

        # Create submit button after defining the submit function
        bottoneSubmit = ctk.CTkButton(
            finestraEdit,
            text="SUBMIT",
            corner_radius=5,
            command=submitModificaPlugin  # Set the command to submit the changes
        )
        bottoneSubmit.pack(pady=20)  # Pack the button

    def rimuoviPlugin(self):
        """
        Removes the selected plugin from the application.
        """
        if self.plugin_selezionato is None:
            messagebox.showwarning("Nessun plugin selezionato", "Seleziona un plugin prima di rimuoverlo.")  # Warning if no plugin is selected
            return
        try:
            self.coreApplicazione.rimuovi_plugin(str(self.plugin_selezionato))  # Remove the plugin from the core application
            self.plugin_selezionato = None  # Reset selected plugin
            self.selected_params = None  # Reset selected parameters
            self.labelInfoPluginSelezionato.configure(text="SELECTED PLUG-IN: None")  # Update the label
        except Exception as e:
            messagebox.showerror("Error", f"Errore nella rimozione del plug-in: {e}")  # Show error message

    def configuraTest(self, edit=True):
        """
        Opens a configuration window for setting up tests or routines.

        Args:
            edit (bool): Indicates whether to edit an existing test or create a new one.
        """
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
            ctk.CTkLabel(finestraRoutine, text="FREQUENCY").pack(pady=10)
            frequencyFrame = ctk.CTkFrame(master=finestraRoutine)
            frequencyFrame.pack(fill="x", pady=1)
            frequency = ctk.CTkEntry(master=frequencyFrame)
            frequency.pack(side="left", fill="x", expand=True)

        # Parameters input
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

        # Submit function for the configuration
        def submit():
            # Initialize an empty dictionary to hold parameters
            params = {}
            i = 0
            # Iterate through the entries in paramsEntry to collect parameter values
            for param in paramsEntry:
                params[self.selected_params[i]] = param.get()
                i+=1

            # Check if we are in edit mode
            if edit:
                self.coreApplicazione.avvia_test(self.plugin_selezionato, params)
            else:
                self.coreApplicazione.crea_routine(self.plugin_selezionato, params, int(frequency.get()))
            # Close the routine window
            finestraRoutine.destroy()

        # Create a submit button that triggers the submit function when clicked
        submitButton =  ctk.CTkButton(master=finestraRoutine, text="SUBMIT", corner_radius=5, command=submit)
        submitButton.pack(pady=50)

    def iniziaTest(self):
        # Check if a plugin has been selected
        if self.plugin_selezionato is None:
            # Show a warning if no plugin is selected
            messagebox.showwarning("No Plugin Selected", "Please select a plugin before starting the test.")
            return
        try:
            # Initialize an empty dictionary for test parameters
            parametriTest = {}
            # Start the test with the selected plugin and parameters
            self.coreApplicazione.avvia_test(self.plugin_selezionato, parametriTest)
        except Exception as e:
            # Show an error message if there is an issue initializing the test
            messagebox.showerror("Error", f"Error initializing the test: {e}")


    def aggiungiPlugin(self, name, idPlugin):
        # Add a new plugin to the plugin_files dictionary
        self.plugin_files[name] = {'id': idPlugin}
        # Update the plugin list display
        self.aggiornaListaPlugin()


    def creaRoutine(self):
        # Configure the test for routine creation
        self.configuraTest(False)


    def notifica(self):
        # Print the current state of the update button
        print("Button state: ", self.bottoneUpdate.cget("state"))
        # Enable the update button if it is currently disabled
        if self.bottoneUpdate.cget("state") == "disabled":
            self.bottoneUpdate.configure(state="normal")


    def cambiaView(self):
        # Toggle between two modes: "p" (plugin) and "t" (test)
        if self.mode == "p":
            self.mode = "t"  # Switch to test mode
            self.coreApplicazione.stop_polling()  # Stop polling for updates
            self.labelCaricaP.pack_forget()  # Hide loading label
            self.bottoneCaricaP.pack_forget()  # Hide loading button

            # Update labels for the test view
            self.labelInfoP.configure(text="LOG DESCRIPTION")
            self.labelInfoPluginSelezionato.configure(text="SELECTED LOG: None")
            self.labelPSelezionabili.configure(text="AVAILABLE LOGS")
            self.labelGestisciP.configure(text="MANAGE LOGS")
            self.bottoneRinominaP.configure(text="EDIT LOG")
            self.bottoneUpdate.pack_forget()  # Hide update button
            self.bottoneView.configure(text="VIEW PLUG-INS")
            self.bottoneRimuoviP.pack_forget()  # Hide remove button
            self.bottoneConfig.pack_forget()  # Hide config button
            self.bottoneStart.pack_forget()  # Hide start button

            # Update the test list display
            self.aggiornaListaTest()
        else:
            self.mode = "p"  # Switch back to plugin mode
            self.coreApplicazione.start_polling()  # Start polling for updates
            self.labelCaricaP.pack(pady=10)  # Show loading label
            self.bottoneCaricaP.pack(pady=10)  # Show loading button

            # Update labels for the plugin view
            self.labelInfoP.pack_forget()  # Hide previous info label
            self.labelInfoP.configure(text="TEST ANALYSIS")
            self.labelInfoPluginSelezionato.pack_forget()  # Hide previous selected plugin label
            self.labelInfoPluginSelezionato.configure(text="SELECTED PLUGIN: None")
            self.labelInfoP.pack(pady=10)  # Show updated info label
            self.labelInfoPluginSelezionato.pack(pady=10)  # Show updated selected plugin label

            self.labelPSelezionabili.pack_forget()  # Hide previous available plugins label
            self.labelPSelezionabili.configure(text="AVAILABLE PLUG-INS")
            self.labelPSelezionabili.pack(pady=10)  # Show updated available plugins label
            self.listaPlugin.pack_forget()  # Hide previous plugin list
            self.listaPlugin.pack(pady=10)  # Show updated plugin list

            self.labelGestisciP.pack_forget()  # Hide previous manage label
            self.labelGestisciP.configure(text="MANAGE PLUG-IN")
            self.labelGestisciP.pack(pady=10)  # Show updated manage label

            self.bottoneRinominaP.pack_forget()  # Hide previous rename button
            self.bottoneRinominaP.configure(text="EDIT PLUGIN")
            self.bottoneRinominaP.pack(pady=10)  # Show updated rename button

            self.bottoneRimuoviP.pack(pady=10)  # Show remove button
            self.bottoneView.configure(text="VIEW TEST LOGS")  # Update view button text
            self.bottoneUpdate.pack(before=self.bottoneView)  # Position update button before view button
            self.bottoneUpdate.configure(state="disabled")  # Disable update button
            self.informazioniTest.pack(pady=10)  # Show test information
            self.bottoneConfig.pack(pady=10)  # Show config button
            self.bottoneStart.pack(pady=10)  # Show start button

            # Update the plugin list display
            self.aggiornaListaPlugin()

# main.py
from core.core import ClientCore
from core.core import UIUpdater
from ui.main_window import MainInterfaccia
import tkinter as tk
from ui.login_window import get_login_info
import customtkinter as ctk

def main():
    # Ottieni le informazioni di login
    ip_address, username, password = get_login_info()

    # Crea la finestra principale
    finestra = ctk.CTk()  # Correzione: nessun argomento per ctk.CTk

    # Inizializza l'UIUpdater e il ClientCore
    uihandler = UIUpdater()
    c = ClientCore('https://' + ip_address + ':5000', uihandler, username, password)

    # Crea l'interfaccia principale
    m = MainInterfaccia(finestra, c)

    # Inizializza l'interfaccia utente
    uihandler.initUI(m)
    m.initUI()

    # Avvia il loop principale dell'applicazione
    finestra.mainloop()

if __name__ == "__main__":
    main()
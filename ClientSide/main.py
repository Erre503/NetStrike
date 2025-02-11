# Punto d'ingresso dell'app
from core.core import ClientCore
from core.core import UIUpdater
from ui.main_window import MainInterfaccia
import customtkinter as ctk

def main(): 
    finestra = ctk.CTk()
    uihandler = UIUpdater()
    c = ClientCore('http://192.168.79.41:5000', uihandler)
    m = MainInterfaccia(finestra, c)
    uihandler.initUI(m)
    m.initUI()

    finestra.mainloop()

if __name__ == "__main__":
    main()
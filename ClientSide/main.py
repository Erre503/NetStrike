# Punto d'ingresso dell'app
from core.core import ClientCore
from core.core import UIUpdater
from ui.main_window import MainInterfaccia
import tkinter as tk

def main():
    finestra = tk.Tk()
    uihandler = UIUpdater(finestra)
    c = ClientCore('http://127.0.0.1:5000', uihandler)
    MainInterfaccia(finestra, c)

    finestra.mainloop()

if __name__ == "__main__":
    main()
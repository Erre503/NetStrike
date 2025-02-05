# Punto d'ingresso dell'app
from core.core import ClientCore
from core.core import UIUpdater
from ui.main_window import MainInterfaccia
import tkinter as tk

def main():
    finestra = tk.Tk()
    uihandler = UIUpdater()
    c = ClientCore('http://192.168.217.40:5000', uihandler)
    m = MainInterfaccia(finestra, c)
    uihandler.initUI(m)
    m.initUI()

    finestra.mainloop()

if __name__ == "__main__":
    main()
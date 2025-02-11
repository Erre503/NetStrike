# main.py
from core.core import ClientCore
from core.core import UIUpdater
from ui.main_window import MainInterfaccia
import tkinter as tk
from ui.login_window import get_ip_address

def main():
    ip_address = get_ip_address()
    finestra = tk.Tk()
    uihandler = UIUpdater()
    c = ClientCore('http://'+ip_address+':5000', uihandler)
    m = MainInterfaccia(finestra, c)
    uihandler.initUI(m)
    m.initUI()

    finestra.mainloop()

if __name__ == "__main__":
    main()

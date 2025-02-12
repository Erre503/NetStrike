# main.py
from core.core import ClientCore
from core.core import UIUpdater
from ui.main_window import MainInterfaccia
import tkinter as tk
from ui.login_window import get_login_info

def main():
    ip_address, username, password = get_login_info()

    finestra = tk.Tk()
    uihandler = UIUpdater()
    c = ClientCore('https://'+ip_address+':5000', uihandler, username, password)
    m = MainInterfaccia(finestra, c)
    uihandler.initUI(m)
    m.initUI()
    finestra.mainloop()


if __name__ == "__main__":
    main()

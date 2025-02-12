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
<<<<<<< HEAD
    c = ClientCore('http://127.0.0.1:5000', uihandler)
=======
    c = ClientCore('http://'+ip_address+':5000', uihandler)
>>>>>>> 585c174d4a54bd1595053b31ae2e13d32768b5a0
    m = MainInterfaccia(finestra, c)
    uihandler.initUI(m)
    m.initUI()

    finestra.mainloop()

if __name__ == "__main__":
    main()

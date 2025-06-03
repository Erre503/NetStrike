# main.py
from core.core import ClientCore
from core.ui_updater import UIUpdater
from ui.main_window import MainInterfaccia
import customtkinter as ctk
from ui.login_window import get_login_info

def main():
    ip_address, username, password = get_login_info()

    finestra = ctk.CTk()
    uihandler = UIUpdater()

    c = ClientCore('https://'+ip_address+':5000', uihandler, username, password)

    m = MainInterfaccia(finestra, c)
    uihandler.initUI(m)
    m.initUI()
    c.start_polling()
    finestra.mainloop()


if __name__ == "__main__":
    main()

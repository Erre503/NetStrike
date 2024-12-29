# Punto d'ingresso dell'app
from core.core import ClientCore
from core.core import UIUpdater
from ui.main_window import UserInterface

# Dummy implementation
def main():
    ui = UserInterface()

    ui_updater = UIUpdater(ui)
    core_client = ClientCore("127.0.0.1",ui_updater)

    print("\n\tSuccessful start")


if __name__ == "__main__":
    main()

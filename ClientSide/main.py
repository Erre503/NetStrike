# main.py
from core.core import ClientCore  # Import the ClientCore class for managing client-server interactions
from core.ui_updater import UIUpdater  # Import the UIUpdater class for updating the user interface
from ui.main_window import MainInterfaccia  # Import the MainInterfaccia class for the main application window
import customtkinter as ctk  # Import the customtkinter library for creating custom GUI elements
from ui.login_window import get_login_info  # Import the function to retrieve login information

def main():
    """
    Main function to initialize and run the application.

    This function retrieves user login information, sets up the main application window,
    initializes the client core, and starts the user interface.
    """
    ip_address, username, password = get_login_info()  # Get the IP address, username, and password from the login window

    finestra = ctk.CTk()  # Create the main application window using customtkinter
    uihandler = UIUpdater()  # Create an instance of the UIUpdater to manage UI updates

    # Initialize the ClientCore with the server URL, UI handler, username, and password
    c = ClientCore('https://' + ip_address + ':5000', uihandler, username, password)

    # Create the main interface window and pass the ClientCore instance to it
    m = MainInterfaccia(finestra, c)
    uihandler.initUI(m)  # Initialize the UI components using the UIUpdater
    m.initUI()  # Initialize the main interface UI components
    c.start_polling()  # Start polling for updates from the server
    finestra.mainloop()  # Start the main event loop for the application

if __name__ == "__main__":
    """
    Entry point of the script.

    This block checks if the script is being run directly (as opposed to being imported as a module).
    If so, it calls the main function to execute the application.
    """
    main()  # Execute the main function

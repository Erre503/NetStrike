"""
Manages the update of the graphical user interface (GUI).

This class provides methods to update various elements
of the user interface, such as the list of plugins, the details of a
selected plugin, and the results of executed tests.

Attributes:
    ui: A reference to the graphical interface to be updated.
        This object represents the UI framework used, such as
        PyQt, Tkinter, or another GUI system.
"""
class UIUpdater:
    """
    Initializes an instance of UIUpdater.

    Args:
        ui: The reference to the graphical interface that will be updated
            through the methods of this class.
    """
    def __init__(self):
        self.ui = None  # Initialize the `ui` attribute to None

    """
    Associates the graphical interface with the UIUpdater instance.

    Args:
        ui: Instance of the UI that will be updated by the methods of this class.

    Effects:
        - The `ui` attribute is updated to point to the specified UI.
    """
    def initUI(self, ui):
        self.ui = ui  # Update the `ui` attribute with the provided instance

    """
    Updates the list in the graphical interface.

    Args:
        items (dict): Data to update the list.
            Expected structure:
            - name (str): Name of the item.
            - id (str): Unique ID of the item.
    """
    def aggiorna_lista(self, items):
        self.ui.svuota_lista()  # Clear the existing list in the interface

        # Add each item to the list
        for item in items:
            self.ui.aggiungi_elemento(item["name"], str(item["id"]))

    """
    Displays the details of the selected item in the graphical interface.

    Args:
        details (dict): A dictionary containing the details.
            Expected structure:
            - description (str): Description of the item.
            - parameters (dict, optional): Parameters as key-value pairs.
    """
    def aggiorna_dettagli(self, details):
        self.ui.mostra_dettagli(details)  # Show the provided details in the interface

    """
    Displays the results of an executed test in the graphical interface.

    Args:
        results (dict): A dictionary containing the test results.
            Expected structure:
            - status (str): Status of the test (e.g., "success", "failed").
            - log (str): Detailed log of the test.
            - datetime (str): Formatted timestamp of the test (e.g., "YYYY-MM-DD HH:MM:SS").
    """
    def aggiorna_risultato_test(self, results):
        # Extract results from the dictionary, providing default values
        status = results.get("status", "unknown")
        log = results.get("log", "")
        datetime = results.get("datetime", "N/A")

        # Display the test results in the interface
        self.ui.mostra_risultato_test(
            status=status,
            log=log,
            datetime=datetime
        )

    """
    Displays the error in the graphical interface.

    Args:
        msg (str): The error message.
    """
    def show_error(self, msg):
        print(f"MESSAGE {msg}")
        self.ui.show_error(msg)

    def notifica(self):
        # Send a notification to the graphical interface
        self.ui.notifica()

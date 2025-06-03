from enum import Enum  # Import Enum class for creating enumerations
import os  # Import os for operating system related functionalities (not used in this code)

class UpdateType(Enum):
    # Enumeration for different types of updates for the graphical interface
    LISTA = 0  # Indicates that the interface should update the list of plugins
    DETTAGLI = 1  # Indicates that the interface should show the details of a plugin
    RISULTATI_TEST = 2  # Indicates that the interface should display the results of a test
    AGGIORNA_LISTA = 3  # Indicates that the interface should refresh the list
    ERROR = 4 # Indicates that the interface should display the error message

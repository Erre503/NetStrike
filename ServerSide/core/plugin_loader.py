import os  # Library for working with application files and directories
import importlib  # Allows dynamic import of modules since file names are unknown
import sys  # Used to modify paths for Python files
import abc
import inspect  # Used to inspect parameters and class definitions
import subprocess  # Used for executing bash files
from pathlib import Path  # Used to get the current file path reference
from datetime import datetime

# Define the folder path for plugins
FOLDER = Path(__file__).resolve().parent.parent / "plugins"

def process_plugin_name(nome_file):
    """
    Processes the plugin file name to separate the name and extension.

    Args:
        nome_file (str): The name of the plugin file.

    Returns:
        tuple: A tuple containing the name and extension of the file.
    """
    processed = nome_file.rsplit('.', 1)  # Split the file name into name and extension
    return processed[0], processed[1]

def rinomina_plugin(nomeVecchio, nomeNuovo):
    """
    Renames a plugin file from the old name to the new name.

    Args:
        nomeVecchio (str): The current name of the file.
        nomeNuovo (str): The new name for the file.

    Returns:
        str: Success or error message.
    """
    try:
        vecchio_path = FOLDER / nomeVecchio  # Get the old file path
        nuovo_path = FOLDER / nomeNuovo  # Get the new file path
        vecchio_path.rename(nuovo_path)  # Rename the file
        return "Plugin renamed successfully."
    except Exception:
        return "Error: Unable to rename the file."

def elimina_plugin(nome):
    """
    Deletes a plugin file.

    Args:
        nome (str): The name of the file to delete.

    Returns:
        str: Success or error message.
    """
    file_path = FOLDER / nome  # Get the file path

    try:
        os.remove(file_path)  # Remove the file
        return "Plugin deleted successfully."
    except FileNotFoundError:
        return f"Error: The file '{file_path}' does not exist."
    except PermissionError:
        return f"Error: Permission denied to delete '{file_path}'."
    except Exception as e:
        return f"Error: Unable to delete the file '{file_path}'. Details: {e}"

def estraiParametriBash(plugin):
    """
    Extracts parameters from a Bash plugin.

    Args:
        plugin (str): The name of the Bash plugin file.

    Returns:
        list: A list of parameters extracted from the plugin or an error message.
    """
    try:
        comando = ["bash", plugin, "get_param"]  # Command to get parameters
        parametri = subprocess.run(comando, capture_output=True, text=True, check=True)  # Run the command
        listaParametri = parametri.stdout.strip().split(", ")  # Process the output
        return listaParametri
    except Exception:
        return "Error extracting parameters from Bash."

def interfacciaBash(content):
    """
    Checks if the required functions are present in the Bash script.

    Args:
        content (str): The content of the Bash script.

    Returns:
        bool: True if all required functions are present, False otherwise.
    """
    functions_to_check = ['set_param', 'get_param', 'execute']  # Required functions
    for x in functions_to_check:
        if x not in content:  # Check for each function
            return False
    return True

def avvia_plugin_bash(plugin, vet_param):
    """
    Executes a Bash plugin with the provided parameters.

    Args:
        plugin (str): The name of the Bash plugin file.
        vet_param (dict): A dictionary of parameters to pass to the plugin.

    Returns:
        str: The output of the executed Bash plugin or an error message.
    """
    try:
        # Prepare the command to execute the Bash script
        shell = "/bin/bash"
        comando = f"bash {plugin}"

        # Prepare the environment variables
        env_vars = {**os.environ, **vet_param}  # Combine existing and new environment variables

        # Execute the command in a shell
        ret = subprocess.run(comando, shell=True, check=True, env=env_vars, executable=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return ret.stdout.decode('utf-8')  # Return the output
    except subprocess.CalledProcessError as e:
        return f"Error executing the Bash plugin: {e}"
    except Exception as e:
        return f"General error: {e}"

def creaPluginPy(nome_file, contenuto):
    """
    Creates a Python plugin file and validates its content.

    Args:
        nome_file (str): The name of the Python file to create.
        contenuto (str): The content of the Python file.

    Returns:
        tuple: A tuple containing a success flag and the parameters if successful, otherwise None.
    """
    file_name = nome_file[:-3]  # Remove the .py extension
    file = FOLDER / nome_file  # Get the file path

    if file.is_file():  # Check if the file already exists
        return False, "Error: The file already exists."

    # Add required import
    full_content = f"from core.interfaccia_plugin import Interfaccia_Plugin \n\n{contenuto}"
        
    try:
        # Write to the file
        file.write_text(full_content)
        
        # Validate through the temporary file
        spec = importlib.util.spec_from_file_location(file_name, file)  # Create a module spec
        modulo = importlib.util.module_from_spec(spec)  # Create a module from the spec
        spec.loader.exec_module(modulo)  # Execute the module

        # Class validation
        if not hasattr(modulo, "Plugin"):  # Check for the Plugin class
            raise AttributeError("Missing 'Plugin' class")

        classe_plugin = modulo.Plugin  # Get the Plugin class

        if not inspect.isclass(classe_plugin):  # Check if it is a class
            raise TypeError("'Plugin' is not a class")

        if not issubclass(classe_plugin, modulo.Interfaccia_Plugin):  # Check inheritance
            raise TypeError("Must inherit from Interfaccia_Plugin")

        if len(classe_plugin.__abstractmethods__) > 0:  # Check for unimplemented abstract methods
            raise NotImplementedError(f"Unimplemented abstract methods: {classe_plugin.__abstractmethods__}")

        # Import the module dynamically
        plugin_module = importlib.import_module('plugins.' + file_name)  # Remove ".py"
        plugin_instance = plugin_module.Plugin()  # Create the plugin instance
        params = plugin_instance.get_param()  # Get parameters from the plugin
        return True, params  # Return success

    except (AttributeError, TypeError, NotImplementedError) as e:
        if file.is_file():
            os.remove(file)  # Remove the file if validation fails
        return False, f"Validation failed: {e}"

    except Exception as e:
        if file.is_file():
            os.remove(file)  # Remove the file if an unexpected error occurs
        return False, f"An unexpected error occurred: {e}"

def creaPluginSh(nome_file, contenuto):
    """
    Creates a Bash plugin file if it meets the required interface.

    Args:
        nome_file (str): The name of the Bash file to create.
        contenuto (str): The content of the Bash file.

    Returns:
        tuple: A tuple containing a success flag and None if successful, otherwise None.
    """
    if nome_file in os.listdir(FOLDER):  # Check if the file already exists
        return False, "Error: The file already exists."
    if interfacciaBash(contenuto):  # Check if the content meets the required interface
        percorso_file = os.path.join(FOLDER, nome_file)  # Get the file path
        with open(percorso_file, "w", encoding="utf-8") as file:  # Write the content to the file
            file.write(contenuto)
        return True, "Bash plugin created successfully."
    else:
        return False, "Error: The content does not meet the required interface."

def creaPlugin(nome_file, contenuto):
    """
    Creates a plugin based on the file extension.

    Args:
        nome_file (str): The name of the file to create.
        contenuto (str): The content of the file.

    Returns:
        tuple: A tuple containing a success flag and parameters if successful, otherwise None.
    """
    if nome_file.endswith('.sh'):  # Check for Bash file
        return creaPluginSh(nome_file, contenuto)
    if nome_file.endswith('.py'):  # Check for Python file
        return creaPluginPy(nome_file, contenuto)
    return False, "Error: Unsupported file type."

def avvia_plugin(nome_plugin, vet_param):
    """
    Executes a plugin based on its file extension.

    Args:
        nome_plugin (str): The name of the plugin file.
        vet_param (dict): A dictionary of parameters to pass to the plugin.

    Returns:
        dict: A dictionary containing the execution result and status.
    """
    res = {}
    res['datetime'] = datetime.now()  # Record the current time
    file_name, extension = process_plugin_name(nome_plugin)  # Process the plugin name
    if extension == 'py':  # If the plugin is a Python file
        try:
            # Dynamically import the Python module
            modulo = importlib.import_module('plugins.' + file_name)  # Remove ".py"
            plugin_instance = modulo.Plugin()  # Create the plugin instance
            plugin_instance.set_param(vet_param)  # Set parameters for the plugin
            res['log'] = plugin_instance.execute()  # Execute the plugin
            res['status'] = 'finished'  # Set status to finished
            return res

        except Exception as e:
            res['log'] = f"Error importing and executing the Python module {nome_plugin}: {e}"  # Error message
            res['status'] = 'failed'  # Set status to failed
            return res

    # If the plugin is a Bash file
    elif extension == 'sh':
        # Check if the file exists
        percorso_file = FOLDER / nome_plugin
        res['log'] = avvia_plugin_bash(percorso_file, vet_param)  # Execute the Bash plugin
        res['status'] = 'finished'  # Set status to finished
        return res
    else:
        res['log'] = "Error: Unsupported plugin type."  # Unsupported plugin type message
        res['status'] = 'failed'  # Set status to failed
        return res
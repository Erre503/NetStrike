import os  # Library for interacting with the operating system
import secrets  # Library for generating secure random numbers

class KeyManager:
    """
    Manages the generation, storage, and retrieval of secure keys.

    This class provides methods to generate a secure random key, store it in an environment variable,
    retrieve it from the environment variable, and regenerate the key.

    Attributes:
        None
    """

    @staticmethod
    def generate_key(length=64):
        """
        Generates a secure random key of the specified length.

        Args:
            length (int): Length of the key to generate. Default is 64 bytes.

        Returns:
            str: A securely generated random key.
        """
        KeyManager.store_key(secrets.token_urlsafe(length))  # Generate and store the key
        return KeyManager.retrieve_key()  # Retrieve and return the stored key

    @staticmethod
    def store_key(key, env_var_name='JWT_SECRET_KEY'):
        """
        Stores the generated key in an environment variable.

        Args:
            key (str): The key to store.
            env_var_name (str): The name of the environment variable. Default is 'JWT_SECRET_KEY'.
        """
        os.environ[env_var_name] = key  # Store the key in the specified environment variable
        print(f"Chiave memorizzata nella variabile d'ambiente '{env_var_name}'.")  # Print confirmation message

    @staticmethod
    def retrieve_key(env_var_name='JWT_SECRET_KEY'):
        """
        Retrieves the key from the specified environment variable.

        Args:
            env_var_name (str): The name of the environment variable. Default is 'JWT_SECRET_KEY'.

        Returns:
            str: The key stored in the environment variable, or None if not found.
        """
        return os.environ.get(env_var_name)  # Return the value of the environment variable

    @staticmethod
    def regenerate_key(env_var_name='JWT_SECRET_KEY'):
        """
        Regenerates the key and updates the environment variable.

        Args:
            env_var_name (str): The name of the environment variable. Default is 'JWT_SECRET_KEY'.
        """
        new_key = KeyManager.generate_key()  # Generate a new key
        KeyManager.store_key(new_key, env_var_name)  # Store the new key in the environment variable
        print("Chiave rigenerata.")  # Print confirmation message

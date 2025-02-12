import os, secrets

class KeyManager:
    """
    Genera una chiave casuale sicura della lunghezza specificata.

    Args:
        length (int): Lunghezza della chiave da generare. Il valore predefinito è 64 byte.

    Returns:
        str: Una chiave casuale generata in modo sicuro.
    """
    @staticmethod
    def generate_key(length=64):
        KeyManager.store_key(secrets.token_urlsafe(length))
        return KeyManager.retrieve_key()

    """
    Memorizza la chiave generata in una variabile d'ambiente.

    Args:
        key (str): La chiave da memorizzare.
        env_var_name (str): Il nome della variabile d'ambiente. Il valore predefinito è 'JWT_SECRET_KEY'.
    """
    @staticmethod
    def store_key(key, env_var_name='JWT_SECRET_KEY'):
        os.environ[env_var_name] = key
        print(f"Chiave memorizzata nella variabile d'ambiente '{env_var_name}'.")

    """
    Recupera la chiave dalla variabile d'ambiente specificata.

    Args:
        env_var_name (str): Il nome della variabile d'ambiente. Il valore predefinito è 'JWT_SECRET_KEY'.

    Returns:
        str: La chiave memorizzata nella variabile d'ambiente, oppure None se non trovata.
    """
    @staticmethod
    def retrieve_key(env_var_name='JWT_SECRET_KEY'):
        return os.environ.get(env_var_name)

    """
    Rigenera la chiave e aggiorna la variabile d'ambiente.

    Args:
        env_var_name (str): Il nome della variabile d'ambiente. Il valore predefinito è 'JWT_SECRET_KEY'.
    """
    @staticmethod
    def regenerate_key(env_var_name='JWT_SECRET_KEY'):
        new_key = KeyManager.generate_key()
        KeyManager.store_key(new_key, env_var_name)
        print("Chiave rigenerata.")

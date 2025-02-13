
import pyotp
import keyring
import html


"""
Sanifica il parametro inserito rimuovendo caratteri HTML potenzialmente dannosi.

Args:
    param (str): Stringa da sanificare. Il valore viene sanificato solo se stringa.

Returns:
    ret (str):
        La stringa sanificata.
"""
def sanitize_input(param : str) -> str:
    if(isinstance(param, str)):
        return html.escape(param);
    return param

"""
Sanifica i valori del dizionario inserito attraverso la funzione sanitize_inputs.

Args:
    input_dict (dict): Dizionario da sanificare.

Returns:
    ret (dict):
        Il dizionario sanificata.
"""
def sanitize_dict(input_dict : dict) -> dict:
    return {key: sanitize_input(value) for key, value in input_dict.items()}

"""
Sanifica i valori della lista inserita attraverso la funzione sanitize_input.

Args:
    input_list (list): Lista da sanificare.

Returns:
    ret (list):
        La lista sanificata.
"""
def sanitize_list(input_list: list) -> list:
    return [sanitize_input(item) for item in input_list]

if __name__ == '__main__':
    #Testing
    keyring.set_password("my_app", "access_token", "token_value")
    print(keyring.get_password("my_app", "access_token"))
    secret = pyotp.random_base32()
    print(f"Segreto per Google Authenticator: {secret}")

    keyring.delete_password("my_app", "access_token")

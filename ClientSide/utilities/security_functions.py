import html, keyring, re
"""
Sanifica il parametro inserito rimuovendo caratteri HTML potenzialmente dannosi.

Args:
    param (str): Stringa da sanificare. Il valore viene sanificato solo se stringa, dizionario o lista.

Returns:
    ret (str):
        La stringa sanificata.
"""
def sanitize_input(param : str) -> str:
    if(isinstance(param, str)):

        return html.escape(param)
    elif(isinstance(param, dict)):
        return sanitize_dict(param)

    elif(isinstance(param, list)):
        return sanitize_list(param)

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

"""
Salva il token JWT fornito nel keyring.

Args:
    token (str): Il token JWT da salvare nel keyring.
"""
def save_token(token):
    keyring.set_password("plugink_token", "jwt_token", token.encode('utf-8'))

"""
Recupera il token JWT precedentemente salvato nel keyring.

Returns:
    str or None:
        Il token JWT se esiste, altrimenti None.
"""
def get_token():
    token = keyring.get_password("plugink_token", "jwt_token")
    if(isinstance(token, bytes)):
        token = token.decode('utf-8')

    return token

"""
Elimina il token JWT dal keyring.

Questa funzione rimuove il token associato al nome di servizio "my_app"
e al nome di chiave "jwt_token", rendendolo non più accessibile.
"""
def clear_token():
    keyring.delete_password("plugink_token", "jwt_token")

"""
Verifica se l'input fornito utilizza solo caratteri consentiti.

Args:
    user_input(str): Input da verificare.

Returns:
    bool:
        True se utilizza solo i caratteri consintiti,
        altrimenti false
"""
def is_valid_input(user_input):
    pattern = r"^[a-zA-Z0-9 _-]+$"
    return bool(re.match(pattern, user_input))

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

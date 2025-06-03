import html  # Library for handling HTML entities

"""
Sanitizes the input parameter by removing potentially harmful HTML characters.

Args:
    param (str): The string to sanitize. The value is sanitized only if it is a string.

Returns:
    str: The sanitized string, or the original value if it is not a string.
"""
def sanitize_input(param: str) -> str:
    if isinstance(param, str):  # Check if the parameter is a string
        return html.escape(param)  # Escape HTML characters to prevent injection
    return param  # Return the original value if it is not a string

"""
Sanitizes the values of the input dictionary using the sanitize_input function.

Args:
    input_dict (dict): The dictionary to sanitize.

Returns:
    dict: The sanitized dictionary with safe values.
"""
def sanitize_dict(input_dict: dict) -> dict:
    return {key: sanitize_input(value) for key, value in input_dict.items()}  # Sanitize each value in the dictionary

"""
Sanitizes the values of the input list using the sanitize_input function.

Args:
    input_list (list): The list to sanitize.

Returns:
    list: The sanitized list with safe values.
"""
def sanitize_list(input_list: list) -> list:
    return [sanitize_input(item) for item in input_list]  # Sanitize each item in the list

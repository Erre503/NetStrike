import html  # Import the html module for escaping HTML characters
import keyring  # Import the keyring module for secure storage of credentials
import re  # Import the re module for regular expression operations

"""
Sanitizes the input parameter by removing potentially harmful HTML characters.

Args:
    param (str): The string to sanitize. The value is sanitized only if it is a string, dictionary, or list.

Returns:
    ret (str):
        The sanitized string.
"""
def sanitize_input(param: str) -> str:
    if isinstance(param, str):
        return html.escape(param)  # Escape HTML characters in the string
    elif isinstance(param, dict):
        return sanitize_dict(param)  # Sanitize the dictionary values

    elif isinstance(param, list):
        return sanitize_list(param)  # Sanitize the list items

    return param  # Return the parameter unchanged if it's not a string, dict, or list

"""
Sanitizes the values of the input dictionary using the sanitize_input function.

Args:
    input_dict (dict): The dictionary to sanitize.

Returns:
    ret (dict):
        The sanitized dictionary.
"""
def sanitize_dict(input_dict: dict) -> dict:
    return {key: sanitize_input(value) for key, value in input_dict.items()}  # Sanitize each value in the dictionary

"""
Sanitizes the values of the input list using the sanitize_input function.

Args:
    input_list (list): The list to sanitize.

Returns:
    ret (list):
        The sanitized list.
"""
def sanitize_list(input_list: list) -> list:
    return [sanitize_input(item) for item in input_list]  # Sanitize each item in the list

"""
Saves the provided JWT token in the keyring.

Args:
    token (str): The JWT token to save in the keyring.
"""
def save_token(token):
    keyring.set_password("plugink_token", "jwt_token", token)  # Store the token in the keyring

"""
Retrieves the previously saved JWT token from the keyring.

Returns:
    str or None:
        The JWT token if it exists, otherwise None.
"""
def get_token():
    return keyring.get_password("plugink_token", "jwt_token")  # Retrieve the token from the keyring

"""
Deletes the JWT token from the keyring.

This function removes the token associated with the service name "plugink_token"
and the key name "jwt_token", making it no longer accessible.
"""
def clear_token():
    keyring.delete_password("plugink_token", "jwt_token")  # Remove the token from the keyring

"""
Checks if the provided input contains only allowed characters.

Args:
    user_input (str): The input to check.

Returns:
    bool:
        True if it contains only allowed characters,
        otherwise False.
"""
def is_valid_input(user_input):
    pattern = r"^[a-zA-Z0-9 _-]+$"  # Define a regex pattern for allowed characters
    return bool(re.match(pattern, user_input))  # Return True if the input matches the pattern

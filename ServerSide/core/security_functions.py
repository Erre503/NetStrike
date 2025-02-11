import pyotp
import keyring

keyring.set_password("my_app", "access_token", "token_value")
print(keyring.get_password("my_app", "access_token"))
secret = pyotp.random_base32()
print(f"Segreto per Google Authenticator: {secret}")

keyring.delete_password("my_app", "access_token")

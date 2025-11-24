import requests
import time
import os

# --- CONFIGURAZIONE ---
# Nel tuo Docker Compose, OPENSKY_USERNAME è il Client ID
# e OPENSKY_PASSWORD è il Client Secret.
CLIENT_ID = os.environ.get('OPENSKY_USERNAME')
CLIENT_SECRET = os.environ.get('OPENSKY_PASSWORD')

# URL specifici
AUTH_URL = "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"
API_BASE_URL = "https://opensky-network.org/api"

def get_access_token():
    """
    Richiede un Token OAuth2 temporaneo usando Client ID e Secret.
    Il token dura 30 minuti.
    """
    if not CLIENT_ID or not CLIENT_SECRET:
        print("ERRORE: Credenziali mancanti nelle variabili d'ambiente.")
        return None

    payload = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    
    try:
        response = requests.post(AUTH_URL, data=payload, timeout=10)
        response.raise_for_status()
        # Restituisce solo la stringa del token
        return response.json().get('access_token')
    except requests.exceptions.RequestException as e:
        print(f"ERRORE Autenticazione OAuth2: {e}")
        if response.text:
            print(f"Dettaglio errore server: {response.text}")
        return None

def get_arrivals_by_airport(airport_code, hours_back=24):
    # 1. Otteniamo il token prima di fare la richiesta dati
    token = get_access_token()
    if not token:
        return []

    # 2. Prepariamo i tempi
    end_time = int(time.time())
    start_time = end_time - (hours_back * 3600)
    
    url = f"{API_BASE_URL}/flights/arrival"
    params = {
        'airport': airport_code,
        'begin': start_time,
        'end': end_time
    }
    
    # 3. Creiamo l'Header con il Bearer Token (la novità fondamentale)
    headers = {
        'Authorization': f"Bearer {token}"
    }

    try:
        # Nota: usiamo 'headers' invece di 'auth'
        print(f"Richiedo dati per {airport_code} usando OAuth2...")
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Errore OpenSky API: {e}")
        # Se è un 401 qui, vuol dire che il token è scaduto o invalido
        if response.status_code == 401:
            print("Token scaduto o non valido.")
        return []

# --- TEST ---
if __name__ == "__main__":
    # Testiamo con un aeroporto
    voli = get_arrivals_by_airport('LICC', hours_back=6) # Catania
    print(f"Voli trovati: {len(voli)}")
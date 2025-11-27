import requests
import time
import os


CLIENT_ID = os.environ.get('OPENSKY_USERNAME')
CLIENT_SECRET = os.environ.get('OPENSKY_PASSWORD')

AUTH_URL = "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"
API_BASE_URL = "https://opensky-network.org/api"

def get_access_token():
  
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
        return response.json().get('access_token')
    except requests.exceptions.RequestException as e:
        print(f"ERRORE Autenticazione OAuth2: {e}")
        if response.text:
            print(f"Dettaglio errore server: {response.text}")
        return None

def get_departures_by_airport(airport_code, hours_back=24):
    token = get_access_token()
    if not token:
        return []
    end_time = int(time.time())
    print(f"End time: {end_time}")
    start_time = end_time - (hours_back * 3600)

    chunk_size = 24 * 3600 

    timeSv = end_time
    flights = []
    while timeSv > start_time:
        sv = timeSv - chunk_size

        if sv < start_time:
            sv = start_time
        url = f"{API_BASE_URL}/flights/departure"
        params = {
            'airport': airport_code,
            'begin': start_time,
            'end': end_time
        }
        headers = {
            'Authorization': f"Bearer {token}"
        }

        try:
            print(f"Richiedo dati per {airport_code} usando OAuth2...")
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            flights.append(response.json())
        except requests.exceptions.RequestException as e:
            print(f"Errore OpenSky API: {e}")
            if response.status_code == 401:
                print("Token scaduto o non valido.")
            return []
        timeSv = sv
    print(f"Totale voli recuperati: {len(flights)}")
    return flights


def get_arrivals_by_airport(airport_code, hours_back=24):
    token = get_access_token()
    if not token:
        return []

    end_time = int(time.time())
    start_time = end_time - (hours_back * 3600)

    chunks = 24*3600
    current_time = end_time

    url = f"{API_BASE_URL}/flights/arrival"
    params = {
        'airport': airport_code,
        'begin': start_time,
        'end': end_time
    }
    
    headers = {
        'Authorization': f"Bearer {token}"
    }

    try:
        print(f"Richiedo dati per {airport_code} usando OAuth2...")
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Errore OpenSky API: {e}")
        if response.status_code == 401:
            print("Token scaduto o non valido.")
        return []

if __name__ == "__main__":
    voli = get_arrivals_by_airport('LICC', hours_back=6) 
    print(f"Voli trovati: {len(voli)}")
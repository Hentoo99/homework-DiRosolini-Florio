import requests
import time
import os
from flask import jsonify


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
    

def opensky_api_request(airport_code, hours_back, flight_type):
    token = get_access_token()
    print(f"Flight type: {flight_type}, Airport: {airport_code}, Hours back: {hours_back}")
    if not token:
        return []
    end_time = int(time.time()) - 1200
    print(f"End time: {end_time}")
    start_time = end_time - (hours_back * 3600)

    chunk_size = 24 * 3600 

    timeSv = end_time
    flights = []
    while timeSv > start_time:
        sv = timeSv - chunk_size
    
        if sv < start_time:
            print("Aggiustamento start time chunk")
            sv = start_time


        url = f"{API_BASE_URL}/flights/{flight_type}"
        params = {
            'airport': airport_code,
            'begin': sv,
            'end': timeSv
        }
        headers = {
            'Authorization': f"Bearer {token}"
        }

        try:
            print(f"Richiedo dati per {airport_code} usando OAuth2...")
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            flights.extend(response.json())
        except requests.exceptions.RequestException as e:
            print(f"Errore OpenSky API: {e}")
            if response.status_code == 401:
                print("Token scaduto o non valido.")
            if response.status_code == 404:
                print("Nessun dato trovato per questo intervallo di tempo.")
        
        timeSv = sv
    print(f"Totale voli recuperati: {len(flights)}")
    return flights

def get_departures_by_airport(airport_code, hours_back=24):
    return opensky_api_request(airport_code, hours_back, "departure")


def get_arrivals_by_airport(airport_code, hours_back=24):
    return opensky_api_request(airport_code, hours_back, "arrival")

if __name__ == "__main__":
    voli = get_arrivals_by_airport('LICC', hours_back=6) 
    print(f"Voli trovati: {len(voli)}")
import flask
import sys, atexit
from pymongo import MongoClient
from apscheduler.schedulers.background import BackgroundScheduler
import collector
import os
import grpc
sys.path.append(os.path.join(os.getcwd(), 'proto')) 
import user_manager_pb2  
import user_manager_pb2_grpc

print("Starting Data Collector Service...")
app = flask.Flask(__name__)
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
client = MongoClient(MONGO_URI)
db = client.flight_data_db

users_interests_collection = db.interests   
flights_collection = db.flights  
print("Connected to MongoDB.")


def update_flight_data():
    print("--- Avvio aggiornamento ciclico voli ---")
    airports = users_interests_collection.distinct("airport_code")
    if not airports:
        print("Nessun aeroporto da monitorare.")
        return
    for airport in airports:
        print(f"Scaricamento dati per: {airport}...")
        flights = get_arrivals_by_airport(airport)
        
        if flights:
            try:
                for f in flights:
                    f['airport_monitored'] = airport
                
                flights_collection.insert_many(flights)
                print(f"Salvati {len(flights)} voli per {airport}")
            except Exception as e:
                print(f"Errore salvataggio Mongo: {e}")


scheduler = BackgroundScheduler()
scheduler.add_job(func=update_flight_data, trigger="interval", hours=12)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

# --- REST API Endpoints ---
# openSky Data Retrieval Endpoint

@app.route('/add_interest', methods=['POST'])
def add_interest():
    print("Received request to add user interest via REST API")
    data = flask.request.get_json()
    email = data.get('email')
    airport_code = data.get('airport_code')
    if not email or not airport_code:
        return flask.jsonify({'status': 'error', 'message': 'Email and airport_code are required'}), 400

    print(f"Verifying user existence for email: {email} via gRPC")
    with grpc.insecure_channel('user-manager:50051') as channel:
        stub = user_manager_pb2_grpc.UserManagerStub(channel)
        response = stub.CheckUserExists(user_manager_pb2.CheckUserExistsRequest(email=email))
        if not response.exists:
            return flask.jsonify({'status': 'error', 'message': 'User does not exist'}), 404
    print(f"Adding interest for email: {email}, airport_code: {airport_code}")
    result = users_interests_collection.update_one(
        {'email': email, 'airport_code': airport_code},
        {'$set': {'email': email, 'airport_code': airport_code}},
        upsert=True
    )
    
    if result.upserted_id:
        print(f"Inserted new interest with id: {result.upserted_id}")
        return flask.jsonify({'status': 'success', 'message': f'Interest for {airport_code} added for {email}'}), 200


    return flask.jsonify({'status': 'Failed already added', 'message': f'Interest for {airport_code} added for {email}'}), 409

@app.route('/rmv_interest', methods=['POST'])
def rmv_interest():
    print("Received request to remove user interest via REST API")
    data = flask.request.get_json()
    email = data.get('email')
    airport_code = data.get('airport_code')

    if not email or not airport_code:
        return flask.jsonify({'status': 'error', 'message': 'Email and airport_code are required'}), 400

    with grpc.insecure_channel('user-manager:50051') as channel:
        stub = user_manager_pb2_grpc.UserManagerStub(channel)
        response = stub.CheckUserExists(user_manager_pb2.CheckUserExistsRequest(email=email))
        if not response.exists:
            return flask.jsonify({'status': 'error', 'message': 'User does not exist'}), 404
    
    result = users_interests_collection.delete_one({'email': email, 'airport_code': airport_code})

    if result.deleted_count == 0:
        return flask.jsonify({'status': 'error', 'message': 'No such interest found'}), 404

    return flask.jsonify({'status': 'success', 'message': f'Interest for {airport_code} removed for {email}'}), 200

@app.route('/list_interests', methods=['POST'])
def list_interests():
    print("Received request to list user interests via REST API")
    data = flask.request.get_json()
    email = data.get('email')
    print(f"Listing interests for email: {email}")
    if not email:
        return flask.jsonify({'status': 'error', 'message': 'Email is required'}), 400

    with grpc.insecure_channel('user-manager:50051') as channel:
        stub = user_manager_pb2_grpc.UserManagerStub(channel)
        response = stub.CheckUserExists(user_manager_pb2.CheckUserExistsRequest(email=email))
        if not response.exists:
            return flask.jsonify({'status': 'error', 'message': 'User does not exist'}), 404

    interests = list(users_interests_collection.find({'email': email}, {'_id': 0, 'airport_code': 1}))
    airport_codes = [interest['airport_code'] for interest in interests]

    return flask.jsonify({'status': 'success', 'interests': airport_codes}), 200


@app.route('/check_user', methods=['POST'])
def check_user():
    print("Received request to check if user exists via REST API")
    data = flask.request.get_json()
    email = data.get('email')
    with grpc.insecure_channel('user-manager:50051') as channel:
        stub = user_manager_pb2_grpc.UserManagerStub(channel)
        response = stub.CheckUserExists(user_manager_pb2.CheckUserExistsRequest(email=email))
        return flask.jsonify({'exists': response.exists})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


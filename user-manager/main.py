import flask
import mysql.connector
import time
import os
import sys
from concurrent import futures
import grpc
import threading
sys.path.append(os.path.join(os.getcwd(), 'proto')) # FONDAMENTALE

import user_manager_pb2       
import user_manager_pb2_grpc  


DB_HOST = 'db'
DB_USER = 'root'
DB_PASSWORD = 'root_password'
DB_NAME = 'user_db'

class UserManagerServicer(user_manager_pb2_grpc.UserManagerServicer):
    def CheckUserExists(self, request, context):
        print("gRPC request to check if user exists")
        data = {'email': request.email}
        exists = get_is_inserted(data)
        print(f"User exists: {exists}")
        return user_manager_pb2.CheckUserExistsResponse(exists=exists)
app = flask.Flask(__name__)


def get_is_inserted(data):
    db_conn = get_db_connection()
    if db_conn.is_connected():
        cursor = db_conn.cursor()
        QUERY = "SELECT * FROM users WHERE email = %s"
        valori = (data['email'], )
        cursor.execute(QUERY, valori)
        result = cursor.fetchone()
        if result:
            print("User already exists in the database")
            return True
    print("User does not exist in the database")
    return False


def run_grpc_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_manager_pb2_grpc.add_UserManagerServicer_to_server(UserManagerServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC server started on port 50051", flush=True)
    server.wait_for_termination()

def get_db_connection():
    retries = 30
    while retries > 0:
        try:
            print(f"Tentativo di connessione a {DB_HOST}...", flush=True)
            conn = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            print("--- CONNESSO AL DB CON SUCCESSO ---", flush=True)
            return conn
        except mysql.connector.Error as err:
            print(f"Errore DB ({err}). Riprovo tra 5 secondi...", flush=True)
            retries -= 1
            time.sleep(5)
    
    raise Exception("Impossibile connettersi al database dopo vari tentativi.")

db_conn = get_db_connection()

@app.route('/')
def home():
    return flask.jsonify({"message": "Welcome to the User Manager API", "db_status": "Connected"})

@app.route('/add_user', methods=['POST'])
def add_user():
    print("Received data for new user")
    if(db_conn.is_connected()):
        if not get_is_inserted(flask.request.json):
            print("Adding new user to the database")
            cursor =  db_conn.cursor()
            data = flask.request.json
            
            QUERY = "INSERT INTO users (email, name, surname) VALUES (%s, %s, %s)"
            valori = (data['email'], data['name'], data['surname'])
            cursor.execute(QUERY, valori)
            db_conn.commit()
            if cursor.rowcount > 0:
                print("User added successfully")
                return flask.jsonify({"status": "User added", "user": data})
            return flask.jsonify({"status": "User not added", "user": data})
        return flask.jsonify({"status": "User already exists", "user": flask.request.json})
    return flask.jsonify({"status": "DB not connected"})



@app.route('/get_user', methods=['POST'])
def get_user():
    print("Received request to get user")
    if(db_conn.is_connected()):
        cursor =  db_conn.cursor(dictionary=True)
        data = flask.request.json
        QUERY = "SELECT * FROM users WHERE email = %s"
        valori = (data['email'], )
        cursor.execute(QUERY, valori)
        result = cursor.fetchone()
        if result:
            print("User retrieved successfully")
            return flask.jsonify({"status": "User found", "user": result})
        return flask.jsonify({"status": "User not found", "email": data['email']})
    return flask.jsonify({"status": "DB not connected"})
    

@app.route('/rmv_user', methods=['POST'])
def rmv_user():
    print("Received request to remove user")
    if(db_conn.is_connected()):
        print("Checking if user exists for removal")
        if get_is_inserted(flask.request.json):
            print("User does not exist, cannot remove")
            cursor =  db_conn.cursor()
            data = flask.request.json
            QUERY = "DELETE FROM users WHERE email = %s"
            valori = (data['email'], )
            cursor.execute(QUERY, valori)
            db_conn.commit()
            if cursor.rowcount > 0:
                print("User removed successfully")
                return flask.jsonify({"status": "User removed", "email": data['email']})
            return flask.jsonify({"status": "User not removed", "email": data['email']})
        return flask.jsonify({"status": "User does not exist", "email": flask.request.json['email']})
    return flask.jsonify({"status": "DB not connected"})

if __name__ == '__main__':
    server = threading.Thread(target=run_grpc_server)
    server.start()
    app.run(debug=True, host='0.0.0.0', port=5000)


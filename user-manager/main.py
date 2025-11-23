import flask
import mysql.connector
import time
import os

app = flask.Flask(__name__)

DB_HOST = os.getenv('DB_HOST', 'db')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'root_password')
DB_NAME = os.getenv('DB_NAME', 'user_db')

def get_db_connection():
    """Prova a connettersi al database finché non ci riesce."""
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
    return flask.jsonify({"status": "User removed", "user_id": 2})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
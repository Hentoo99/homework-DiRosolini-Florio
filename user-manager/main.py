import flask


app = flask.Flask(__name__)
@app.route('/')
def home():
    print("Received request at home endpoint")
    return flask.jsonify({"message": "Welcome to the User Manager API"})

@app.route('/add_user', methods=['POST'])
def add_user():
    print("Received request to add user")
    data = flask.request.json
    print(data)
    return flask.jsonify({"status": "User added", "user": data})

@app.route('/get_user/', methods=['POST'])
def get_user():
    print
    return flask.jsonify({"status": "User retrieved", "user": {"id": 1, "name": "John Doe"}})

@app.route('/rmv_user', methods=['POST'])
def rmv_user():
    print("Received request to remove user")
    return flask.jsonify({"status": "User removed", "user_id": 2})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
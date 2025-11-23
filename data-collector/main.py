import flask

app = flask.Flask(__name__)
@app.route('/')
def home():
    return flask.jsonify({"message": "Welcome to the User Manager API"})

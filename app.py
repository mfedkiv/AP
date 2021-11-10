from flask import Flask
from API.eventAPI import eventQuery

app = Flask(__name__)

app.register_blueprint(eventQuery)

if __name__ == "__main__":
    app.run(debug=True)

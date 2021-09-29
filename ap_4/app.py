from flask import Flask

app = Flask(__name__)


@app.route('/api/v1/hello-world/25')
def index():
    return "Hello World 25"


if __name__ == "__main__":
    app.run(debug=True)

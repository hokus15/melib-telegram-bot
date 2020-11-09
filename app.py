from flask import Flask, request

app = Flask(__name__)


@app.route('/')
def index():
    print(request)
    return '.'


if __name__ == '__main__':
    app.run(threaded=True)

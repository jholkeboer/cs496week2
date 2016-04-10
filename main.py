from flask import Flask
import time
app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello Cloud! The current time is: %s' % time.strftime("%I:%M:%S")


@app.errorhandler(404)
def page_not_found(e):
    return '404 Not Found.', 404


@app.errorhandler(500)
def application_error(e):
    return 'Error: {}'.format(e), 500

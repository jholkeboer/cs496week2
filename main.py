from flask import Flask
from flask import render_template
from flaskext import wtf
from flaskext.wtf import validators
import time
app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello Cloud! The current time is: %s' % time.strftime("%I:%M:%S")

@app.route('/new', methods=['GET'])
def new():
    return render_template('add_recipe.html')
    
# @app.route('/add', methods=['POST'])
# def add():
#     return ""

# @app.route('/edit', methods['POST'])
# def edit():
#     return ""

# @app.route('/all', methods['GET'])
# def all():
#     return ""

@app.errorhandler(404)
def page_not_found(e):
    return '404 Not Found.', 404


@app.errorhandler(500)
def application_error(e):
    return 'Error: {}'.format(e), 500

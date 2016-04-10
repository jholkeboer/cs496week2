import time
from flask import Flask
from flask import render_template, redirect
from flaskext import wtf
from flaskext.wtf import validators
from google.appengine.ext import db
from flaskext import wtf
from flaskext.wtf import validators
from models import Recipe
app = Flask(__name__)
app.secret_key='unsafe'
app.DEBUG=True
app.CSRF_ENABLED=True
app.CSRF_SESSION_LKEY='unsafe'

class RecipeForm(wtf.Form):
    name = wtf.TextField('Name')
    under30 = wtf.BooleanField('Under 30 minutes to make?')
    category = wtf.TextField('Category')
    ingredients = wtf.TextAreaField('Ingredients')
    instructions = wtf.TextAreaField('Instructions')


@app.route('/')
def hello():
    return 'Hello Cloud! The current time is: %s' % time.strftime("%I:%M:%S")

@app.route('/new', methods=['GET', 'POST'])
def new():
    form = RecipeForm()
    if form.validate_on_submit():
        recipe = Recipe(name = form.name.data,
                        under30 = form.under30.data,
                        category = form.category.data,
                        ingredients = form.ingredients.data,
                        instructions = form.instructions.data)
        recipe.put()
        print "Recipe saved."
        return redirect('/all')
    return render_template('add_recipe.html', form=form)
    
# @app.route('/add', methods=['POST'])
# def add():
#     return ""

# @app.route('/edit', methods['POST'])
# def edit():
#     return ""

@app.route('/all', methods=['GET'])
def all():
    # recipes = Recipe.all()
    recipes = db.GqlQuery("SELECT * FROM Recipe")
    for r in recipes:
        print r
    return render_template('view_recipes.html', recipes=recipes)

@app.errorhandler(404)
def page_not_found(e):
    return '404 Not Found.', 404


@app.errorhandler(500)
def application_error(e):
    return 'Error: {}'.format(e), 500

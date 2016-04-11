import time
from flask import Flask
from flask import render_template, redirect, request
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
    category = wtf.RadioField('Category', choices=[('breakfast','Breakfast'),('lunch','Lunch'),('dinner','Dinner')])
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
        time.sleep(1)
        return redirect('/all')
    return render_template('add_recipe.html', form=form)

@app.route('/edit', methods=['GET','POST'])
def edit():
    key = request.args.get('key')
    recipe = Recipe.get(key)
    form = RecipeForm()
    category = str(recipe.category)
    print category
    if request.method == 'GET':
        recipe = Recipe.get(key)
        if recipe:
            form.name.data = recipe.name
            form.under30.data = recipe.under30
            # form.category.default = recipe.category
            form.ingredients.data = recipe.ingredients
            form.instructions.data = recipe.instructions
            form.key = recipe.key()
    elif form.validate_on_submit():
        recipe.name = form.name.data
        recipe.under30 = form.under30.data
        recipe.category = form.category.data
        recipe.ingredients = form.ingredients.data
        recipe.instructions = form.instructions.data
        recipe.put()
        print "Recipe edited."
        time.sleep(1)
        return redirect('/all')
    return render_template('edit_recipes.html', recipe=recipe, form=form, category=category)        

@app.route('/delete', methods=['GET'])
def add():
    key = request.args.get('key')
    print 'deleting key %s' % key
    recipe = Recipe.get(key)
    recipe.delete()
    time.sleep(1)
    return redirect('/all')


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

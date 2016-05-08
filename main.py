import time
import json
from flask import Flask
from flask import render_template, redirect, request
from flaskext import wtf
from flaskext.wtf import validators
from google.appengine.ext import db
from flaskext import wtf
from flaskext.wtf import validators
from models import Recipe, Ingredient
from factual import Factual
from factual.utils import circle
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

#####################################
# FACTUAL API ACCESS FOR ASSIGNMENT 4
#####################################

# load creds from client_secrets.json
secrets_file = open('client_secrets.json', 'r')
factual_creds = json.loads(secrets_file.read())
secrets_file.close()

api_key = factual_creds['api_key']
api_secret = factual_creds['api_secret']

factual = Factual(api_key, api_secret)

# route to hit Factual api
# based on Factual documentation: https://github.com/Factual/factual-python-driver
@app.route('/mobile/factual', methods=['POST'])
def factual_restaurants():
    latitude = float(request.form.get('latitude'))
    longitude = float(request.form.get('longitude'))
    search_term = request.form.get('search_term')
    if not latitude or not longitude:
        return json.dumps({"error": "No location provided"}), 500
    if not search_term:
        return json.dumps({"error": "No search term provided"}), 500
    
    radius = 1000
    
    places = factual.table('places')
    
    # look up restaurants near location
    result = places.search(search_term).geo(circle(latitude, longitude, radius)).data()
    return json.dumps(result), 200

# route to display JQuery mobile page
@app.route('/mobile/home', methods=['GET'])
def mobile_home():
    return render_template('mobile_home.html')

#####################################
# API ROUTES FOR ASSIGNMENT 3 PART 2
#####################################

@app.route('/recipes/all', methods=['GET'])
def api_all_recipes():
    # returns the names and keys of all recipes in the system
    recipes = db.GqlQuery("SELECT * FROM Recipe")
    
    recipeList = []
    for r in recipes:
        recipeList.append({'name': r.name, 'key': str(r.key())})

    return json.dumps({'status': 'OK', 'recipes': recipeList}), 200

@app.route('/recipes', methods=['GET'])
def recipes():
    # get a specific recipe
    key = request.args.get('key')
    recipe = Recipe.get(key)
    print recipe
    
    if not recipe:
        return json.dumps({'error': 'Recipe not found'}), 500
    
    recipe_object = {'name': recipe.name,
                     'prepTime': recipe.prepTime,
                     'instructions': recipe.instructions}
    ingredientList = []
    for i in recipe.ingredients:
        ing = Ingredient.get(i)
        ingredientList.append({'ing_name': ing.name, 'ing_key': str(ing.key())})
    
    recipe_object['ingredients'] = ingredientList
    
    return json.dumps({'status': 'OK', 'recipe': recipe_object}), 200

@app.route('/recipes/new', methods=['POST'])
def recipes_new():
    # inserts a new recipe
    
    if not request.args.get('ingredients'):
        return json.dumps({"error": "No ingredients provided"}), 500
        
    if not request.args.get('instructions'):
        return json.dumps({"error": "No instructions provided"}), 500
    
    recipeName = request.args.get('name')
    
    if not recipeName:
        return json.dumps({"error": "No name provided"}), 500
    
    prepTime = request.args.get('prepTime')
    
    if not prepTime:
        return json.dumps({"error": "No prepTime provided"}), 500

    category = request.args.get('category')
    ingredientList = request.args.get('ingredients').split(',')
    ingredientList = [x.lower() for x in ingredientList]
    instructionList = request.args.get('instructions').split(',')
    

    
    # error handling
    if prepTime.isdigit():
        prepTime = int(prepTime)
        if prepTime <= 0:
            return json.dumps({"error": "Invalid prep time"}), 500
    else:
        return json.dumps({"error": "Invalid prep time"}), 500
        
    if category not in ['breakfast', 'lunch', 'dinner']:
        return json.dumps({"error": "Invalid category.  Valid categories are breakfast, lunch, and dinner"}), 500

    if len(ingredientList) < 1:
        return json.dumps({"error": "Need at least one ingredient"}), 500

    if len(instructionList) < 1:
        return json.dumps({"error": "Need at least one instruction"}), 500
    
    # get ingredient keys
    ingredient_keys = []
    new_ingredients = []
    for ingName in ingredientList:
        ings = db.GqlQuery("SELECT * FROM Ingredient WHERE name = :1", ingName)
        result_count = 0
        for item in ings:
            result_count += 1
            ingredient_keys.append(item.key())
        if result_count == 0:
            new_ingredients.append(ingName)
   
    newRecipe = Recipe(name = recipeName,
                    prepTime = prepTime,
                    category = category,
                    ingredients = [],
                    instructions = instructionList) 
    newRecipe.put()
    recipeKey = newRecipe.key()
    
    # create new ingredients if necessary
    for n in new_ingredients:
        newIngredient = Ingredient(name=n, usedIn=[recipeKey])
        newIngredient.put()
        ingredient_keys.append(newIngredient.key())
    newRecipe.ingredients = ingredient_keys
    
    newRecipe.put()
    
    return json.dumps({'status': "OK", 'message': "Recipe saved successfully"}), 200

@app.route('/ingredients', methods=['GET'])
def ingredients():
    # returns the list of Recipe keys which include the given ingredient name
    ingredientName = request.args.get('ingredientName')
    if not ingredientName:
        return json.dumps({'error': "Invalid request parameter."}), 500
    
    # see if the ingredient exists in the database
    ingredient = db.GqlQuery("SELECT * FROM Ingredient WHERE name = :1", ingredientName)
    result_count = 0
    for item in ingredient:
        result_count += 1
        ingredient_key = item.key()
    if not ingredient_key:
        return json.dumps({'error': "Ingredient not found"}), 500

    # look up recipes that contain that ingredient
    recipe_count = 0
    recipe_list = []
    recipes = db.GqlQuery("SELECT * FROM Recipe WHERE ingredients = :1", ingredient_key)
    for r in recipes:
        recipe_count += 1
        print r
        recipe_list.append(str(r.key()))
    
    return json.dumps({'status': 'OK', 'recipeList': recipe_list}), 200

@app.route('/recipes/add_ingredient', methods=['PUT'])  
def recipes_add_ingredient():
    # associates an ingredient with a recipe
    recipe_key = request.args.get('recipe')
    ingredient_key = request.args.get('ingredient')
    
    recipe = Recipe.get(recipe_key)
    
    if not recipe:
        return json.dumps({'error': 'Recipe not found'}), 500
    
    ingredient = Ingredient.get(ingredient_key)
    if not ingredient:
        return json.dumps({'error': 'Ingredient not found.'}), 500
    
    if ingredient.key() in recipe.ingredients:
        return json.dumps({'status': 'Ingredient already in recipe.'}), 200
    
    # if the ingredient is not already associated, associate it
    recipe.ingredients.append(ingredient.key())
    recipe.put()
    
    # add the recipe to the ingredient's list of recipes that use it
    if recipe.key() not in ingredient.usedIn:
        ingredient.usedIn.append(recipe.key())
        ingredient.put()
    
    return json.dumps({'status': 'Associated ingredient and recipe successfully'}), 200

@app.route('/recipes/delete', methods=['DELETE'])
def recipes_delete():
    # deletes a recipe from the datastore    
    key = request.args.get('recipe')
    recipe = Recipe.get(key)
    
    if not recipe:
        return json.dumps({'error': 'Attempted to delete recipe that does not exist'}), 500
    
    recipe.delete()
    
    # remove recipe from 'usedIn' property of ingredients
    ingredients = db.GqlQuery("SELECT * FROM Ingredient WHERE usedIn = :1", recipe.key())
    for i in ingredients:
        i.usedIn.remove(recipe.key())
        i.put()
    
    return json.dumps({'status': 'Deleted successfully'}), 200










#################################
# LEGACY WEB INTERFACE ROUTES from previous assignment
#################################

@app.route('/')
def hello():
    return redirect('/all')



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
            # form.ingredients.data = recipe.ingredients
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
        for i in r.ingredients:
            print i

    return render_template('view_recipes.html', recipes=recipes)

@app.errorhandler(404)
def page_not_found(e):
    return '404 Not Found.', 404


@app.errorhandler(500)
def application_error(e):
    return 'Error: {}'.format(e), 500


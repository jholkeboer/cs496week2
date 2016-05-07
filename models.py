from google.appengine.ext import db
import json


class Recipe(db.Model):
    name = db.StringProperty(required=True)
    prepTime = db.IntegerProperty(required=True)
    category = db.TextProperty(required=True)
    ingredients = db.ListProperty(db.Key, required=True)
    instructions = db.StringListProperty(required=True)

class Ingredient(db.Model):
    name = db.StringProperty(required=True)
    usedIn = db.ListProperty(db.Key)
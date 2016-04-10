from google.appengine.ext import db


class Recipe(db.Model):
    name = db.StringProperty(required=True)
    under30 = db.BooleanProperty(required=True)
    category = db.TextProperty(required=True)
    ingredients = db.TextProperty(required=True)
    instructions = db.TextProperty(required=True)
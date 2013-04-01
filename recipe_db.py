__author__ = 'Artiom'

from tools import *
from google.appengine.ext import ndb
from google.appengine.api import memcache


def top_recipes(update=False):
    key = 'top_recipes'
    recipes = memcache.get(key)
    if recipes is None or update:
        recipes = Recipe.query().order('-created')
        recipes = list(recipes)
        memcache.set(key, recipes)
    return recipes


def get_recipe_key(recipe_name):
    """

    :param recipe_name:
    :return: key for given recipe name
    """
    key = Recipe.get_by_id(recipe_name).key()
    return key

def get_recipe_by_name(recipe_name):
    """

    :param recipe_name:
    :return:
    """
    p = Recipe.get_by_id(recipe_name)

    return p


class Recipe(ndb.Model):
    owner = ndb.StringProperty(required=True)
    #recipe_name = db.StringProperty(required = True)
    content = ndb.TextProperty(required=True)
    category = ndb.TextProperty(required=True)
    title = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    small_picture = ndb.BlobProperty()
    big_picture = ndb.BlobProperty()
    avatar = ndb.BlobProperty()

    def render(self, noPictures=True):
        """
        Render base_recipe.html
        :param noPictures: default True. True = do not show the pictures
        :return:
        """
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("base_recipe.html", p=self, noPictures=noPictures)


class YourRecipe(ndb.Model):
    owner = ndb.StringProperty(required=True)
    #recipe_name = db.StringProperty(required = True)
    content = ndb.TextProperty(required=True)
    category = ndb.TextProperty(required=True)
    title = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    small_picture = ndb.BlobProperty()
    big_picture = ndb.BlobProperty()
    avatar = ndb.BlobProperty()

    def render(self, noPictures=True):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("base_recipe.html", p=self, noPictures=noPictures)


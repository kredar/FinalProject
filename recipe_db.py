__author__ = 'Artiom'

from tools import *
from defines import *
from google.appengine.ext import ndb
from google.appengine.api import memcache
import logging
from models import Pictures


class Recipe(ndb.Model):
    owner = ndb.StringProperty(required=True)
    content = ndb.TextProperty(required=True)
    category = ndb.StringProperty(required=True, indexed=True)
    title = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    picture_key = ndb.StringProperty()

    def render(self, noPictures=True):
        """
        Render base_recipe.html
        :param noPictures: default True. True = do not show the pictures
        :return:
        """
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("base_recipe.html", p=self, noPictures=noPictures)

    @classmethod
    def add_recipe(cls, name, owner, content, title, category):
        """

        :param name:
        :param owner:
        :param content:
        :param title:
        :param category:
        :return:
        """
        Recipe(id=name, owner=owner, content=content, title=title, category=category).put()
        if owner == ADMIN:
            Recipe.my_top_recipes(True)
        else:
            Recipe.your_top_recipes(True)
        #p.put()
        return True

    @classmethod
    def get_recipes_by_category(cls, category, is_admin):
        if is_admin:
            if category == "All":
                return Recipe.my_top_recipes()
            else:
                recipes = Recipe.query(Recipe.category == category, Recipe.owner == ADMIN).fetch(10)
                return recipes
        else:
            if category == "All":
                return Recipe.your_top_recipes()
            else:
                return Recipe.query(Recipe.category == category, Recipe.owner != ADMIN).fetch(10)

    def update_recipe(self, r_id, owner, content, title, category):
        p = Recipe(id=r_id, owner=owner, content=content, title=title, category=category).put()
        #p.put()
        return True

    @classmethod
    def get_recipe_by_name(cls, recipe_name):
        """

        :param recipe_name:
        :return:
        """
        p = Recipe.get_by_id(recipe_name)
        return p

    @classmethod
    def my_top_recipes(cls, update=False):
        key = 'my_top_recipes'
        recipes = memcache.get(key)
        if recipes is None or update:
            recipes = Recipe.query(Recipe.owner == ADMIN).fetch(10)
            memcache.set(key, recipes)
        return recipes

    @classmethod
    def your_top_recipes(cls, update=False):
        key = 'your_top_recipes'
        recipes = memcache.get(key)
        if recipes is None or update:
            recipes = Recipe.query(Recipe.owner != ADMIN).fetch(10)
            memcache.set(key, recipes)
        return recipes

    @classmethod
    def get_recipe_key(cls, recipe_name):
        """

        :param recipe_name:
        :return: key for given recipe name
        """
        key = Recipe.get_by_id(recipe_name).key()
        return key



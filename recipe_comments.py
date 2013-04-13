__author__ = 'Artiom'

from tools import *
from google.appengine.ext import ndb
from google.appengine.api import memcache
import logging
from recipe_db import *


class Recipe_comments(ndb.Model):
    submitter = ndb.StringProperty(required=True)
    recipe = ndb.KeyProperty(kind=Recipe)
    comment = ndb.TextProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def add_comment(cls, submitter, recipe_name, comment):
        recipe = get_recipe_by_name(recipe_name)
        Recipe_comments(submitter=submitter, recipe=recipe.key, comment=comment).put()
        Recipe_comments.get_comments_for_recipe(recipe_name, True)
        Recipe_comments.get_comments_for_recipe(recipe_name, True)

        return True

    @classmethod
    def get_comments_for_recipe(cls, recipe_name, update=False):
        key = str(recipe_name) + 'comments'
        logging.error("key %s" % key)
        comments = memcache.get(key)
        if comments is None or update:
            recipes = Recipe_comments.query(Recipe_comments.recipe == Recipe.get_recipe_by_name(recipe_name).key).order(-Recipe_comments.created).fetch(10)
            memcache.set(key, recipes)

        return comments

    def edit_comment(self, comment):
        self.comment = comment
        self.put()
        return True






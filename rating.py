__author__ = 'Artiom'

import logging

from google.appengine.ext import ndb
from google.appengine.api import memcache
from recipe_db import *


def calcAverageRating(ratings):
    """

    :param ratings: list of ratings entities
    :return: Average rating
    """
    rate_dict = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5}
    average_rating = 0
    if ratings:
        counter = 0
        for rate in ratings:
            average_rating += int(rate_dict[rate.rating])
            counter += 1
        if counter > 0:
            return float(average_rating) / counter
        else:
            return None
    else:
        return None


def ratingsForRecipe(recipe_name, update=False):

    """

    :param recipe_name:
    :param update:
    :return:
    """
    rating = memcache.get(recipe_name)
    if (rating is None) or (update is True):
        recipe = get_recipe_by_name(recipe_name)
        ratings = Rating.query(Rating.recipe == recipe.key)
        #db.GqlQuery("SELECT * FROM Rating WHERE recipe_name = :1" , recipe_name)
        averageRating = calcAverageRating(ratings)
        memcache.set(recipe_name, averageRating)
    return rating


def update_rating(recipe_name, submitter, rating_value):
    """

    :param recipe_name:
    :param submitter:
    :param rating_value:
    :return:
    """
    recipe = get_recipe_by_name(recipe_name)
    ratings = Rating.query(Rating.submitter == submitter, Rating.recipe == recipe.key)

    ##ratings = recipe.ratings.fetch(1000)
    #ratings.filter('submitter =', submitter)
    #ratings.filter('recipe =', recipe)
    updated = False
    if ratings:

        for rate in ratings:
            if rate.submitter == submitter:
                rate.rating = rating_value
                rate.put()
                updated = True
                ratingsForRecipe(recipe_name, True)
    if not updated:
        rate = Rating(recipe=recipe.key, submitter=submitter, rating=rating_value)
        rate.put()
        ratingsForRecipe(recipe_name, True)
    return True


def getRating(recipe_name):

    """

    :param recipe_name:
    :return:
    """
    rating = ratingsForRecipe(recipe_name)
    if rating:
        return rating
    else:
        return None


class Rating(ndb.Model):
    submitter = ndb.StringProperty(required=True)
    recipe = ndb.KeyProperty(kind=Recipe)#, collection_name='ratings', required=True)
    rating = ndb.TextProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)



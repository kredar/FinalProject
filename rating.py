__author__ = 'Artiom'

import logging

from google.appengine.ext import db
from google.appengine.api import memcache
from recipe_db import *

def calcAverageRating(ratings):
    rate_dict = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5}
    average_rating = 0
    if ratings:
        counter = 0
        for rate in ratings:

            #logging.error('Rating %s' % rate.rating)
            average_rating += int(rate_dict[rate.rating])
            counter += 1
        if counter > 0:
            return float(average_rating) / counter
        else:
            return None
    else:
        return None


def ratingsForRecipe(recipe_name, update=False):
    '''
    Memcache for ratings
    '''
    #key = recipe_name
    rating = memcache.get(recipe_name)
    logging.error("_______________About to calculating average ratings___ %s" % update)
    if (rating is None) or (update is True):
        #logging.error("_______________calculating average ratings_________________________")
        recipe = get_recipe_by_name(recipe_name)
        ratings = recipe.ratings.fetch(1000)  #db.GqlQuery("SELECT * FROM Rating WHERE recipe_name = :1" , recipe_name)
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
    ratings = Rating.all()
    recipe = get_recipe_by_name(recipe_name)
    #ratings = recipe.ratings.fetch(1000)
    ratings.filter('submitter =', submitter)
    ratings.filter('recipe =', recipe)
    updated = False
    if ratings:

        for rate in ratings:
            if rate.submitter == submitter:
                #logging.error("____________________upadting ratings")
                rate.rating = rating_value
                rate.put()
                updated = True
                ratingsForRecipe(recipe_name, True)
    if not updated:
        rate = Rating(recipe=recipe, submitter=submitter, rating=rating_value, recipe_name=recipe_name)
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


class Rating(db.Model):
    submitter = db.StringProperty(required = True)
    recipe = db.ReferenceProperty(Recipe, collection_name='ratings', required=True)
    rating = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)



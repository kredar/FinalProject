__author__ = 'Artiom'

import logging

from google.appengine.ext import db
from google.appengine.api import memcache


def calcAverageRating(ratings):
    rate_dict = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5}
    average_rating = 0
    if ratings:
        counter = 0
        for rate in ratings:

            logging.error('Rating %s' % rate.rating)
            average_rating  = average_rating + int(rate_dict[rate.rating])
            counter = counter + 1
        if counter > 0:
            return (float(average_rating)/counter)
        else:
            return None
    else:
        return None





def ratingsForRecipe(recipe_name, update = False):
    '''
    Memcache for ratings
    '''
    key = recipe_name
    rating = memcache.get(key)
    if rating is None or update:
        ratings = db.GqlQuery("SELECT * FROM Rating WHERE recipe_name = :1" , recipe_name)
        averageRating = calcAverageRating(ratings)
        memcache.set(key, averageRating)
    return rating


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
    recipe_name = db.StringProperty(required = True)
    rating = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)



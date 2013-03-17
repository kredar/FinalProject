#__author__ = 'Artiom'

from tools import *
from google.appengine.ext import db
from google.appengine.api import memcache


def blog_key(name='default'):
    return db.Key.from_path('blogs', name)


def top_posts(update=False):
    """
        Getting last 10 posts from memchace

    :param update: if True memcache will be updated
    :return: return 10 last blog post
    """
    key = 'top'
    posts = memcache.get(key)
    if posts is None or update:
        posts = Post.all().order('-created')
        posts = list(posts)
        memcache.set(key, posts)
    return posts


def permalink_post(key):
    """

    :param key: blog ID
    :return: return post with given key
    """
    post = memcache.get(key)
    if post is None:
        db_key = db.Key.from_path('Post', int(key), parent=blog_key())
        post = db.get(db_key)
        memcache.set(key, post)
    return post


class Recipe(db.Model):
    owner = db.StringProperty(required=True)
    #recipe_name = db.StringProperty(required = True)
    content = db.TextProperty(required=True)
    category = db.TextProperty(required=True)
    title = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    small_picture = db.BlobProperty()
    big_picture = db.BlobProperty()
    avatar = db.BlobProperty()

    def render(self, noPictures=True):
        """
        Render base_recipe.html
        :param noPictures: default True. True = do not show the pictures
        :return:
        """
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("base_recipe.html", p=self, noPictures=noPictures)


class YourRecipe(db.Model):
    owner = db.StringProperty(required=True)
    #recipe_name = db.StringProperty(required = True)
    content = db.TextProperty(required=True)
    category = db.TextProperty(required=True)
    title = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    small_picture = db.BlobProperty()
    big_picture = db.BlobProperty()
    avatar = db.BlobProperty()

    def render(self, noPictures=True):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("base_recipe.html", p=self, noPictures=noPictures)


class Post(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p=self)

    def as_dict(self):
        time_fmt = '%c'
        d = {'subject': self.subject,
             'content': self.content,
             'created': self.created.strftime(time_fmt),
             'last_modified': self.last_modified.strftime(time_fmt)}
        return d


class Comment(db.Model):
    post_id = db.StringProperty(required=True)
    submitter = db.StringProperty(required=True)
    comment = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p=self)


class Pictures(db.Model):
    page_name = db.StringProperty(required=True)
    description = db.TextProperty()
    small_picture = db.BlobProperty()
    big_picture = db.BlobProperty()
    avatar = db.BlobProperty()



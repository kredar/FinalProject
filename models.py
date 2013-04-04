#__author__ = 'Artiom'

from tools import *
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import images
import logging

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
        for post in posts:
            logging.error(post)
        memcache.set(key, posts)
    return posts


def permalink_post(key, update=False):
    """

    :param key: blog ID
    :return: return post with given key
    """
    post = memcache.get(key)
    if post is None or update:
        db_key = db.Key.from_path('Post', int(key), parent=blog_key())
        post = db.get(db_key)
        memcache.set(key, post)
    return post


def edit_post(post_id, subject, content):
    """

    :param post_id:
    :param subject:
    :param content:
    """
    db_key = db.Key.from_path('Post', int(post_id), parent=blog_key())
    post = db.get(db_key)
    post.subject = subject
    post.content = content
    post.put()
    top_posts(True)
    permalink_post(post_id, True)


def remove_post(post_id):
    """
        Removes
    :param post_id:
    :return:
    """
    #TODO: create 404 page
    db_key = db.Key.from_path('Post', int(post_id), parent=blog_key())
    post = db.get(db_key)
    # if not post:
    #     BasicHandler.error(404)
    #     return
    post.delete()
    top_posts(True)




def get_comments_for_post(post_id):
    """

    :param post_id:
    :return:
    """
    comments = db.GqlQuery("SELECT * FROM Comment WHERE post_id = :1 ORDER BY created DESC LIMIT 10", post_id)
    return comments


def add_comment_for_post(post_id, submitter, comment):
    """

    :param post_id:
    :param submitter:
    :param comment:
    """
    com = Comment(post_id=post_id, submitter=submitter, comment=comment)
    com.put()


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

    @classmethod
    def add_picture(cls, image, title=None):

        image.resize(width=1024)
        image.im_feeling_lucky()
        big_pic = image.execute_transforms(output_encoding=images.JPEG)
        image.resize(500,400)
        small_pic = image.execute_transforms(output_encoding=images.JPEG)
        image = rescale(img_data=image, width=75,height=75)
        if title:
            for i in range(1,10,1):
                logging.error("LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL")
            picture = Pictures(page_name=title)
        else:
            picture = Pictures(page_name="Creation")
        picture.small_picture = db.Blob(small_pic)
        picture.big_picture = db.Blob(big_pic)
        picture.avatar = db.Blob(image)
        picture.put()

        return picture.key()





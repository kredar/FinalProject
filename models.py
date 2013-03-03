#__author__ = 'Artiom'

from tools import *
from google.appengine.ext import db

class Recipe(db.Model):
    owner = db.StringProperty(required = True)
    recipe_name = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    category = db.TextProperty(required= True)
    title = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add = True)
    small_picture = db.BlobProperty()
    big_picture = db.BlobProperty()
    avatar = db.BlobProperty()

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("base_recipe.html", p = self)


class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p = self)

    def as_dict(self):
        time_fmt = '%c'
        d = {'subject': self.subject,
             'content': self.content,
             'created': self.created.strftime(time_fmt),
             'last_modified': self.last_modified.strftime(time_fmt)}
        return d

class Comment(db.Model):
    post_id = db.StringProperty(required = True)
    submitter = db.StringProperty(required = True)
    comment = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p = self)



class Pictures(db.Model):
    page_name=db.StringProperty(required = True)
    description=db.TextProperty()
    small_picture = db.BlobProperty()
    big_picture = db.BlobProperty()
    avatar = db.BlobProperty()



import os
import re
import random
import hashlib
import hmac

import logging
import time
import urllib

from string import letters
from time import gmtime, strftime

import webapp2
import jinja2

from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.api import mail
#from google.appengine.ext import blobstore
from google.appengine.api import images
from google.appengine.api import users
from google.appengine.ext.webapp import blobstore_handlers


from models import *
from defines import *
from tools import *
from rating import *
from recipe_db import *
from recipe_comments import *


#template_dir = os.path.join(os.path.dirname(__file__), 'templates')
#jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
#                               autoescape = True)




# def render_str(template, **params):
#     t = jinja_env.get_template(template)
#     return t.render(params)

def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

def render_post(response, post):
    response.out.write('<b>' + post.subject + '</b><br>')
    response.out.write(post.content)



def make_salt(length = 5):
    return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)

def users_key(group = 'default'):
    """

    :param group:
    :return:
    """
    return db.Key.from_path('users', group)

def valid_username(username):
    return username and USER_RE.match(username)
def valid_password(password):
    return password and PASS_RE.match(password)

def valid_email(email):
    return not email or EMAIL_RE.match(email)


class BasicHandler(webapp2.RequestHandler):


    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user_name'] = self.get_current_username()
        params['logged_in'] = self.userLogedIn()
        params['logoutLink'] = self.logoutLink()
        params['isUserAdmin'] = self.isUserAdmin()
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        #logging.error(str(user.key().id()))
        current_user = user.name
        # logging.error(str(user.key().id()))
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        if self.user:
            self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')


    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))
        if self.user:
            self.current_user = User.by_id(int(uid)).name
        else:
            self.current_user = None

    def get_user_name(self):
        if self.read_secure_cookie('user_id') != None:
            return self.read_secure_cookie('user_id')

    def userLogedIn(self):
        if self.user or users.get_current_user():
            return True
        else:
            return False

    def get_current_username(self):
        if self.user:
            return self.user.name
        elif users.get_current_user():
            logging.error("USER:  %s" %users.get_current_user().nickname() )
            return users.get_current_user().nickname()
        else:
            return None

    def logoutLink(self):
        if self.userType() == 0:
            return '/logout'
        else:
            return users.create_logout_url('/')

    def userType(self):
        if self.user:
            return 0
        else:
            return 1
    def isUserAdmin(self):

        """
        Checks if user is admin

        :return: True - user is Admin, else return False
        """
        if self.userLogedIn():
            if self.userType() == 0:
                if self.user.name == 'admin':
                    return True
                else:
                    return False
            elif self.userType() == 1:
                if users.is_current_user_admin():
                    return True
                else:
                    return False
        else:
            return None


class MainPage(BasicHandler):
    def get(self):
        self.redirect('/Welcome')


class User(db.Model):
    name = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent = users_key())

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email = None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent = users_key(),
                    name = name,
                    pw_hash = pw_hash,
                    email = email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u



class BlogFront(BasicHandler):
    def get(self):
        """


        """
        posts =  top_posts(True)
        posts =  top_posts()

        self.render('front.html', posts = posts)






class PostPage(BasicHandler):

    def get(self, post_id):
        post = permalink_post(post_id)#db.get(key)
        if not post:
            self.error(404)
            return
        comments = get_comments_for_post(post_id)
        self.render("permalink.html", post = post , comments = comments)#, q_time = last_acc_time )

    def post(self, post_id):
        comment = self.request.get('comment')

        if self.userLogedIn():
            if comment:
                if self.get_current_username():
                    add_comment_for_post(post_id, self.get_current_username(), comment)
                    self.redirect("/blog/%s" %post_id)
                else:
                    self.write("No user")
        else:
            self.redirect("/login")


class NewPost(BasicHandler):

    def get(self):
        if self.isUserAdmin():
            self.render("newpost.html")
        else:
            self.redirect("/login")

    def post(self):
        if not self.isUserAdmin():
            self.redirect('/blog')

        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            p = Post(parent = blog_key(), subject = subject, content = content)
            p.put()
            top_posts(True)

            self.redirect('/blog/%s' % str(p.key().id()))

        else:
            error = "subject and content, please!"
            self.render("newpost.html", subject=subject, content=content, error=error)


class EditPostPage(BasicHandler):


    def get(self,post_id):
        if self.isUserAdmin():
            post = permalink_post(post_id)
            if not post:
                self.error(404)
                return
            self.render("newpost.html", subject = post.subject, content = post.content)
        else:
            self.redirect("/login")


    def post(self, post_id):
        if not self.userLogedIn():
            self.redirect('/blog')

        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            edit_post(post_id, subject, content)
            self.redirect('/blog/%s' % post_id)
        else:
            error = "subject and content, please!"
            self.render("newpost.html", subject=subject, content=content, error=error)


class RemovePostPage(BasicHandler):
    def get(self,post_id):
        if self.isUserAdmin():
            remove_post(post_id)
            self.redirect('/blog')
        else:
            self.redirect("/login")


class Signup(BasicHandler):
    next_url='/'
    def get(self):
        next_url=self.request.headers.get('refer','/')
        # logging.error("next url %s" % next_url)
        self.render("signup-form.html", next_url = next_url)

    def post(self):

        have_error = False


        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username = self.username,
                      email = self.email)

        if not valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password(self.password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('signup-form.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        raise NotImplementedError


class Register(Signup):
    def done(self):
        #make sure the user doesn't already exist
        next_url = str(self.request.get('next_url'))
        if not next_url or next_url.startswith('/login'):
            next_url='/'
        u = User.by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('signup-form.html', error_username = msg)
        else:
            u = User.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.redirect(next_url)

class LoginGoogleUser(BasicHandler):
    def get(self):
        user = users.get_current_user()



class Login(BasicHandler):
    def get(self):

        next_url=self.request.headers.get('referer','/')

        user = users.get_current_user()
        if user:
            greeting = ("Welcome, %s! (<a href=\"%s\">sign out</a>)" % (user.nickname(), users.create_logout_url(next_url)))
        else:
            greeting = ("<a href=\"%s\">Sign in using your google account</a>." % users.create_login_url(next_url))

        #self.response.out.write("<html><body>%s</body></html>" % greeting)

        self.render('login-form.html' , next_url = next_url, google_login_link = users.create_login_url(next_url))


    def post(self):

        next_url = str(self.request.get('next_url'))

        if not next_url or next_url.startswith('/login'):
            next_url='/Welcome'


        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect(next_url)
        else:
            msg = 'Invalid login'
            self.render('login-form.html', error = msg, next_url = next_url, google_login_link = users.create_login_url(next_url))

class Logout(BasicHandler):
    def get(self):
        if users.get_current_user():
            users.create_logout_url('/logout')
        elif self.user:
            self.logout()
            next_url=self.request.headers.get('referer','/')
            self.redirect(next_url)
        else:
            self.redirect('/login')


class CacheFlush(BasicHandler):
    def get(self):
        memcache.flush_all()
        self.redirect('/welcome')

class Welcome(BasicHandler):
    def get(self):
        self.render('welcome.html')


class AllRecipesPage(BasicHandler):
    def get(self):
        self.render('all_recipes.html')



class MyRecipesList(BasicHandler):
    def get(self):
        """This

        """
        category = self.request.get('category')
        recipes = Recipe.get_recipes_by_category(category)

        if recipes:
            self.render('recipes.html', isLogedIn = self.userLogedIn(), recipes=recipes, categories=filter_categories)
        else:
            self.redirect('/Welcome')

    def post(self):
        """This

        """
        category=self.request.get('filter')
        self.redirect("/my_recipes?category=%s" % category)


class YourRecipesList(BasicHandler):
    def get(self):
        """This

        """
        category = self.request.get('category')
        recipes = YourRecipe.get_recipes_by_category(category)

        if recipes:
            self.render('recipes.html', isLogedIn = self.userLogedIn(), recipes=recipes, categories=filter_categories)
        else:
            self.redirect('/Welcome')

    def post(self):
        """This

        """
        category=self.request.get('filter')
        self.redirect("/your_recipes?category=%s" % category)

class AddRecipe(BasicHandler):
    def get(self):
        if self.userLogedIn():
            self.render("edit_recipe.html", newrecipe = True, content="", s = self, categories = recipe_categories )
        else:
            self.redirect('/login')

    def post(self):
        error = None
        if not self.userLogedIn():
            self.redirect('/login')

        content = self.request.get('content')
        title= self.request.get('title')
        category = self.request.get('category')
        logging.error("Page title %s" % title)
        pagename = "/" + title.replace(" ", "")
        logging.error("Page name %s" % pagename)
        regex = re.compile(r'/([a-zA-Z0-9_-]+)$', re.UNICODE)
        r = regex.search(pagename)

        if r is None:
            error = "Recipe title should include only letters and digits"
        elif ( self.isUserAdmin() and get_recipe_by_name(pagename)):
        #     p=Recipe.get_by_key_name(pagename)
        #     if p:
            error = "This recipe page already exist, please use other name"
        #         self.render("edit_recipe.html", pagename = "", title = title, content="", s = self, categories = recipe_categories , error=error)
        #
        elif ( not self.isUserAdmin() and YourRecipe.get_recipe_by_name(pagename)):
        #     p=Recipe.get_by_key_name(pagename)
        #     if p:
            error = "This recipe page already exist, please use other name"
        #         self.render("edit_recipe.html", pagename = "", title = title, content="", s = self, categories = recipe_categories , error=error)
        #
        elif content and title and error == None:
            #p=Recipe.get_by_key_name(page_name)
            #if p:
            #    p.content=content
            #    p.title=title
            #else:
            if (self.isUserAdmin()):
                p = add_recipe(id = pagename, owner = str(self.get_user_name()), content = content, title = title, category = category)
            else:
                p = YourRecipe.add_recipe(name = pagename, owner = str(self.get_user_name()), content = content, title = title, category = category)
            #photo = self.request.get('img')
            # 'file' is file upload field in the form
            #blob_info = upload_files[0]
            #blob_info = upload_files[0]
            #self.redirect('/serve/%s' % blob_info.key())

            #p.photo = db.Blob(photo)

            #h = History(page_name = page_name, content = content)
            #p.put()
            #h.put()
            page_link='/recipes%s' % pagename
            # logging.error(page_name)
            self.redirect(str(page_link))
            #self.redirect('/serve/%s' % blob_info.key())
            #self.redirect('/?' + urllib.urlencode(
            #    {'guestbook_name': guestbook_name}))
        elif not content:
            error = "Recipe content, please!"
            #self.render("newpost.html", subject=subject, content=content, error=error)
            #self.render("edit_recipe.html", title = title, content="", s = self, categories = recipe_categories , error=error)
        elif not title:
            error = "Recipe title, please!"
            #self.render("newpost.html", subject=subject, content=content, error=error)
            #self.render("edit_recipe.html", content=content, s = self, categories = recipe_categories , error=error)
            #upload_files = self.get_uploads('img')
        if error:
            self.render("edit_recipe.html", content=content, s = self, categories = recipe_categories , error=error)


class EditRecipe(BasicHandler):#,blobstore_handlers.BlobstoreUploadHandler):

    def get(self, page_name):
        #page_name_l=page_name
        if self.userLogedIn():
            p=get_recipe_by_name(page_name)
            #img_url= blobstoreService.createUploadUrl("/recipes/_edit%s" %page_name)
            #upload_url = blobstore.create_upload_url('/upload')
            #logging.error("Upload URL %s" % upload_url)
            if p:
                self.render("edit_recipe.html", content=p.content, s = self, title = p.title, categories = recipe_categories)
            else:
                self.render("edit_recipe.html", content="", s = self, categories = recipe_categories )

        else:
            self.redirect('/login')

    def post(self, page_name):
        #self.redirect('/')
        if not self.userLogedIn():
            self.redirect('/login')

        #subject = self.request.get('subject')
        content = self.request.get('content')
        title= self.request.get('title')
        category = self.request.get('category')
        # logging.error("Page name %s" % page_name)
        if content and title:
            p=get_recipe_by_name(page_name)
            if p:
                p.content=content
                p.title=title
                p.put()
            else:
                #p = Recipe(key_name = page_name  , owner = str(self.get_user_name()), content = content, title = title, recipe_name = page_name , category = category)
                add_recipe(id=page_name, owner=str(self.get_user_name()), content=content, title=title, category=category)
                #photo = self.request.get('img')
              # 'file' is file upload field in the form
            #blob_info = upload_files[0]
            #blob_info = upload_files[0]
            #self.redirect('/serve/%s' % blob_info.key())

            #p.photo = db.Blob(photo)

            #h = History(page_name = page_name, content = content)

            #h.put()
            page_link='/recipes%s' % page_name
            # logging.error(page_name)
            self.redirect(str(page_link))
            #self.redirect('/serve/%s' % blob_info.key())
            #self.redirect('/?' + urllib.urlencode(
            #    {'guestbook_name': guestbook_name}))
        elif not content:
            error = "Recipe content, please!"
            #self.render("newpost.html", subject=subject, content=content, error=error)
            self.render("edit_recipe.html", title = title, content="", s = self, categories = recipe_categories , error=error)
        else:
            error = "Recipe title, please!"
            #self.render("newpost.html", subject=subject, content=content, error=error)
            self.render("edit_recipe.html", content=content, s = self, categories = recipe_categories , error=error)
        #upload_files = self.get_uploads('img')



class RecipePage(BasicHandler):

    def get(self, page_name):
        for i in range(1,10,1):
            logging.error(page_name)
        edit_link="/recipes/_edit%s" % page_name
        for i in range(1,10,1):
            logging.error(edit_link)
        if page_name:
            p = get_recipe_by_name(page_name)


            if p:
                rating = getRating(page_name)
                rating = getRating(page_name)
                comments = Recipe_comments.get_comments_for_recipe(page_name)
                #comments = Recipe_comments.get_comments_for_recipe(page_name)
                self.render("singleRecipe.html", page = p , edit_link = edit_link, s = self, rating = rating, comments=comments)
            else:
                self.redirect(edit_link)


    def post(self, page_name):
        rating = self.request.get('rating')
        comment = self.request.get('comment')
        if self.userLogedIn():
            if rating:
                update_rating(page_name, self.get_current_username(), rating)
                self.redirect('/recipes%s' %page_name)
            if comment:
                Recipe_comments.add_comment(self.get_current_username(), recipe_name=page_name, comment=comment)
                self.redirect('/recipes%s' %page_name)
        else:
            self.redirect('/login')


class Gallery(BasicHandler):
    def get(self):
        recipes = Pictures.all()
        self.render("gallery.html", recipes = recipes)



class About(BasicHandler):
    def get(self):
        #Contact form should prevent spammers
        #FormURL = 'http://example.tld/contact.html'
       # if os.environ['HTTP_REFERER'] !=  FormURL: return
        self.render("underconstruction.html")

class ContactUs(BasicHandler):
    def get(self):
        self.render("contact.html")
    def post(self):
        #contact_config = dclab.get_yaml_config('contact.yaml')
        name = self.request.get('contact_name')
        email = self.request.get('email')
        subject = self.request.get('subject')
        message= self.request.get('message')
        #self.validate_post(name, email, message)

        #sender_line = '%s <%s>' % (contact_config['sender_name'], contact_config['sender_email'])
        #receiver_line = '%s <%s>' % (contact_config['receiver_name'], contact_config['receiver_email'])

        sender_line = 'Artiom Kreimer <kreimer.artiom@gmail.com>'
        receiver_line = 'Artiom Kreimer <kreimer.artiom@gmail.com>'
        # Send the email now
        msg = mail.EmailMessage(sender=sender_line, subject= "New email from contact us form") #contact_config['subject_line'])
        msg.to = receiver_line
        #msg.body = contact_config['message_body'] % (name, name, email, subject, message)
        msg.body = """new email from %(name)s %(message)s""" % {"name" : name, "message" : message}

        msg.send()
        self.redirect('/Welcome')

#class BlogFront(BasicHandler):
#    def get(self):
#        #self.render("underconstruction.html")
#        def get(self):
#            posts = greetings = Post.all().order('-created')
#
#            self.render('front.html', posts = posts)

#class UploadPage(BasicHandler):
#
#    def get(self):
#        upload_url = blobstore.create_upload_url('/upload')
#        if self.user:
#            next_url=self.request.headers.get('referer','/')
#            logging.error("next url1 %s" %next_url)
#            self.render("pic_upload.html", upload_url=upload_url, page_name = next_url)
#        else:
#            self.redirect('/login')


class UploadPage(BasicHandler):

    def get(self):
        #upload_url = blobstore.create_upload_url('/upload')
        if self.userLogedIn():
            next_url=self.request.headers.get('referer','/')
            # logging.error("next url1 %s" %next_url)
            self.render("pic_upload.html", upload_url='/upload', page_name = next_url)
        else:
            self.redirect('/login')

# def rescale(img_data, width, height, halign='middle', valign='middle'):
#
#     """Resize then optionally crop a given image.
#
#     Attributes:
#       img_data: The image data
#       width: The desired width
#       height: The desired height
#       halign: Acts like photoshop's 'Canvas Size' function, horizontally
#               aligning the crop to left, middle or right
#       valign: Verticallly aligns the crop to top, middle or bottom
#
#     """
#     image = img_data#images.Image(img_data)
#
#     desired_wh_ratio = float(width) / float(height)
#     wh_ratio = float(image.width) / float(image.height)
#
#     if desired_wh_ratio > wh_ratio:
#         # resize to width, then crop to height
#         image.resize(width=width)
#         image.execute_transforms()
#         trim_y = (float(image.height - height) / 2) / image.height
#         if valign == 'top':
#             image.crop(0.0, 0.0, 1.0, 1 - (2 * trim_y))
#         elif valign == 'bottom':
#             image.crop(0.0, (2 * trim_y), 1.0, 1.0)
#         else:
#             image.crop(0.0, trim_y, 1.0, 1 - trim_y)
#     else:
#         # resize to height, then crop to width
#         image.resize(height=height)
#         image.execute_transforms()
#         trim_x = (float(image.width - width) / 2) / image.width
#         if halign == 'left':
#             image.crop(0.0, 0.0, 1 - (2 * trim_x), 1.0)
#         elif halign == 'right':
#             image.crop((2 * trim_x), 0.0, 1.0, 1.0)
#         else:
#             image.crop(trim_x, 0.0, 1 - trim_x, 1.0)
#
#     return image.execute_transforms()

class UploadHandler(BasicHandler):#blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        next_url = str(self.request.get("page_name"))
        if not next_url or next_url.startswith('/login'):
            next_url='/'
        image = images.Image(self.request.get('img'))  # 'file' is file upload field in the form
        page_url=re.search('recipes(/(?:[a-zA-Z0-9_-]+/?)*)', next_url)
        regex = re.compile("recipes(/(?:[a-zA-Z0-9_-]+/?)*)")
        r = regex.search(next_url)
        if page_url:
            recipe=get_recipe_by_name(str(page_url.groups()[0]))
            if recipe:
                # recipe.small_picture = db.Blob(small_pic)
                # recipe.big_picture = db.Blob(big_pic)
                # recipe.avatar =  db.Blob(avatar)

                recipe.picture_key = str(Pictures.add_picture(image,recipe.title,next_url))
                recipe.put()

                self.redirect(next_url)
        else:
            Pictures.add_picture(image,"Creation")
            self.redirect('/gallery')


class ImageAv(webapp2.RequestHandler):
    def get(self):
        page = db.get(self.request.get('img_id'))
        #logging.error("page %s" % page.small_picture)
        if page.avatar:
            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(page.avatar)
        else:
            self.response.out.write('No image')
            #self.response.headers['Content-Type'] = 'image/png'
            #self.response.out.write(page.small_picture)

class Image(webapp2.RequestHandler):
    def get(self):
        page = db.get(self.request.get('img_id'))

        #logging.error("page %s" % page.small_picture)
        if page.small_picture:
            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(page.small_picture)
        else:
            self.response.out.write('No image')
            #self.response.headers['Content-Type'] = 'image/png'
            #self.response.out.write(page.small_picture)

class ImageB(webapp2.RequestHandler):
    def get(self):
        page = db.get(self.request.get('img_id'))
        #logging.error("page %s" % page.big_picture)
        if page.big_picture:
            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(page.big_picture)
        else:
            self.response.out.write('No image')
            #self.response.headers['Content-Type'] = 'image/png'
            #self.response.out.write(page.small_picture)


class Tools(BasicHandler):
    def get(self):
        self.render('tools.html')


app = webapp2.WSGIApplication([('/img', Image),
                               ('/imgB', ImageB),
                               ('/imgAv', ImageAv),
                               ('//?', MainPage),
                               ('//?Welcome', Welcome),
                               ('/upload', UploadHandler),
                               ('/signup', Register),
                               ('/login', Login),
                               ('/logout', Logout),
                              # ('/serve/([^/]+)?', ServeHandler),
                              ('/my_recipes',MyRecipesList),
                              ('/your_recipes',YourRecipesList),
                               ('/recipes/_upload', UploadPage),
                               ('/recipes/addrecipe', AddRecipe),
                               ('/recipes/_edit' + PAGE_RE, EditRecipe),
                               ('/recipes' + PAGE_RE, RecipePage),
                               ('/gallery', Gallery),
                               ('/recipes', AllRecipesPage),
                               ('/about', About),
                               ('/contact', ContactUs),
                               ('/blog/?', BlogFront),
                               ('/blog/edit/([0-9]+)', EditPostPage),
                               ('/blog/remove/([0-9]+)', RemovePostPage),
                               ('/blog/([0-9]+)', PostPage),
                               ('/blog/newpost', NewPost),
                                ('/flush', CacheFlush),
                                ('/tools', Tools),
                               ],
                              debug=True)


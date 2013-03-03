__author__ = 'Artiom'

from models import *
from tools import *

class RecipesList(BasicHandler):


    def get(self):
        #if self.user:
        #recipes=db.GqlQuery("SELECT * FROM Recipe ORDER BY DESC LIMIT 10")
        recipes = Recipe.all().order('-created')
        #logging.error(page_name)

        if recipes:
        #self.render("edit_recipe.html", page_name = page_name, content=p.content, s = self)
            self.render('recipes.html', recipes = recipes)
            #else:
            #    self.render("edit_recipe.html", page_name = page_name, content="", s = self )
            # q_time = quered_time)

            #else:
            #    self.redirect('/login')
from google.appengine.ext.webapp import blobstore_handlers

class EditRecipe(BasicHandler):#,blobstore_handlers.BlobstoreUploadHandler):
    #page_name_l=""
    def get(self, page_name):
        #page_name_l=page_name
        if self.user:
            p=Recipe.get_by_key_name(page_name)
            #img_url= blobstoreService.createUploadUrl("/recipes/_edit%s" %page_name)
            #upload_url = blobstore.create_upload_url('/upload')
            #logging.error("Upload URL %s" % upload_url)
            if p:
                self.render("edit_recipe.html", content=p.content, s = self, title = p.title)
            else:
                self.render("edit_recipe.html", content="", s = self,  )

        else:
            self.redirect('/login')

    def post(self, page_name):
        #self.redirect('/')
        if not self.user:
            self.redirect('/login')

        #subject = self.request.get('subject')
        content = self.request.get('content')
        title= self.request.get('title')
        # logging.error("Page name %s" % page_name)
        if content:
            p=Recipe.get_by_key_name(page_name)
            if p:
                p.content=content
                p.title=title
            else:
                p = Recipe(key_name = page_name  , owner = str(self.get_user_name()), content = content, title = title, recipe_name = page_name)

                #photo = self.request.get('img')
                # 'file' is file upload field in the form
            #blob_info = upload_files[0]
            #blob_info = upload_files[0]
            #self.redirect('/serve/%s' % blob_info.key())

            #p.photo = db.Blob(photo)

            #h = History(page_name = page_name, content = content)
            p.put()
            #h.put()
            page_link='/recipes%s' % page_name
            # logging.error(page_name)
            self.redirect(str(page_link))
            #self.redirect('/serve/%s' % blob_info.key())
            #self.redirect('/?' + urllib.urlencode(
            #    {'guestbook_name': guestbook_name}))
        else:
            error = "Page content, please!"
            self.render("newpost.html", subject=subject, content=content, error=error)
            #upload_files = self.get_uploads('img')



class RecipePage(BasicHandler):

    def get(self, page_name):
        #self.write("Have a nice day %s" %page_name)
        edit_link="/recipes/_edit%s" % page_name
        #history_link="/_history%s" % page_name

        if page_name:
            #db_page = db.Key.from_path('Post', int(key), parent=blog_key())
            #db_pages = db.GqlQuery("SELECT * FROM Recipe WHERE name = :1 ", page_name)
            p=Recipe.get_by_key_name(page_name)
            if p:
                #self.render('base_recipe.html', page_name = page_name, p = p)
                #b_key = BlobKey(p.picture)
                #self.redirect('/serve/%s' % b_key)
                #self.response.out.write('<div><img src="img?img_id=%s"></img>' % p.key())
                # logging.error("Image %s " % p.small_picture)
                self.render("singleRecipe.html", page = p , edit_link = edit_link, s = self)
                #self.response.out.write("""<img src="image?img_id=%s"></img>""" % p.key())
            else:
                self.redirect(edit_link)

#class RecipesList(BasicHandler):
#    def get(self):
#        self.render("underconstruction.html")



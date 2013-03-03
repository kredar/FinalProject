__author__ = 'Artiom'

import json

#class JsonBlogFront(BasicHandler):
#    def get(self):
#        posts = Post.all().order('-created')
#        #self.render('front.html', posts = posts)
#        post_list=list()
#        for post in posts:
#            post_list.append(postToJson(post))
#        self.response.headers['Content-Type'] = "application/json"
#        self.response.out.write(json.dumps(post_list))


def postToJson(post):
    time_created=post.created.strftime("%a, %d %b %Y %H:%M:%S ")
    time_modified=post.last_modified.strftime("%a, %d %b %Y %H:%M:%S ")
    json_str={}
    json_str['content']=post.content
    json_str['subject']=post.subject
    json_str['created']=time_created
    json_str['last_modified']=time_modified
    return json_str


class JsonPostPage(BlogHandler):
    def get(self, post_id):
        post_number=post_id.split(".")[0]
        key = db.Key.from_path('Post', int(post_number), parent=blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return
            #{"content": "again", "created": "Tue May  8 23:04:17 2012", "last_modified": "Tue May  8 23:04:17 2012", "subject": "the suit is back!"}
        self.response.headers['Content-Type'] = "application/json"

        #self.response.out.write(json.dumps({'content' : post.content, 'subject' : post.subject,'created' : time_created, 'last_modified' : time_modified}))

        self.response.out.write(json.dumps(postToJson(post)))



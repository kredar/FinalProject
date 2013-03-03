__author__ = 'Artiom'


class BasicHandler(webapp2.RequestHandler):

    #current_user = None;

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))
        logging.error('Coockie should be set %s %s' % (name, cookie_val) )

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        #logging.error(str(user.key().id()))
        current_user = user.name
        # logging.error(str(user.key().id()))
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
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


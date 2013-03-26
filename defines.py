import re

secret = 'artiom'

last_queried_time = 0;
permalink_access_time = {}
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
PAGE_RE = r'(/(?:[a-zA-Z0-9!_-]+/?)*)' # From Udacityr'(/(?:[a-zA-Z0-9_-]+/?)*)'

recipe_categories = {'General', 'Cake', 'Cookies', 'Pie', 'Single Serve'}
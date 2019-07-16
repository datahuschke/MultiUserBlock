"""
main.py renders the landing page and handles Login/Logout/Register
it also defines who handles which URL

A sessions variable is used globally to check wether someone is logged in or
not, which affects certain elements of the HTML (e.g. login-link)
This variable should always read the username from the cookie, because if you
just use an empty variable in render(session=session) this will work the same
was as with "session={}" whereas if you use the user object and call .name on
it you get the error "name not defined for none"

known problem/issus:
importing all sub-modules from one main-module doesn't work, I tried:
1.1) in main.py: from app.py.blog import *
1.2) in app/py/blog/__init__.py: __all__ = ["blogpost", "user", etc..]
2.1) same as 1) for app.py.secure import *
Why is that so?
"""
import webapp2
from google.appengine.ext import db

from app.handler import Handler
from app.py.blog.uservalidator import SignupValidator
from app.py.blog.user import User
from app.py.blog.comments import NewComment, EditComment, DeleteComment
from app.py.blog.blogpost import NewPost, PermaLink, AllPosts, Blogpost
from app.py.blog.blogpost import EditPost, DeletePost

global session


class MainPage(Handler):
    def get(self):
        query = "SELECT * FROM Blogpost ORDER BY created DESC LIMIT 10"
        contents = db.GqlQuery(query)
        session = self.get_username_from_cookie()
        self.render("index.html", contents=contents,
                    session=session, like_params={})

    def post(self):
        pid = int(self.request.get("pid"))
        post = Blogpost.get_by_id(pid)
        u = self.current_user()
        if not u:
            self.redirect('/login')
        else:
            like_params = u.like(post)
            if not like_params:
                self.redirect('/')
            else:
                query = "SELECT * FROM Blogpost ORDER BY created DESC LIMIT 10"
                contents = db.GqlQuery(query)
                self.render("index.html", contents=contents,
                            session=u.name, like_params=like_params)


class Welcome(Handler):
    def get(self):
        username = self.get_username_from_cookie()
        session = username
        if username:
            self.render("welcome.html", username=username, session=session)
        else:
            self.redirect('/login')


class Signup(Handler):
    def get(self):
        session = self.get_username_from_cookie()
        self.render("signup.html", params={}, errors={}, session=session)

    def post(self):
        params = self.post_params()
        errors = SignupValidator().errors(params)
        if any(errors.itervalues()):
            session = self.get_username_from_cookie()
            self.render("signup.html", params=params, errors=errors,
                        session=session)
        else:
            self.set_cookie(params['username'], 'username')
            if not params['email']:
                u = User.register(params['username'], params['password'])
            else:
                u = User.register(params['username'], params['password'],
                                  params['email'])
            u.put()
            self.redirect('/welcome')

    def post_params(self):
        permitted_params = ['username', 'password', 'verify', 'email']
        return {key: self.request.get(key) for _,
                key in enumerate(permitted_params)}


class Login(Handler):
    def get(self):
        u = self.current_user()
        if u:
            self.redirect('/welcome')
        else:
            self.render("login.html", params={}, errors={}, session={})

    def post(self):
        params = self.post_params()
        if User.login(params['username'], params['password']):
            self.set_cookie(params['username'], 'username')
            self.redirect('/welcome')
        else:
            errors = {}
            errors['username'] = "Invalid login"
            errors['password'] = "Invalid login"
            self.render("login.html", params={}, errors=errors,
                        session={})

    def post_params(self):
        permitted_params = ['username', 'password']
        return {key: self.request.get(key) for _,
                key in enumerate(permitted_params)}


class Logout(Handler):
    def get(self):
        self.response.delete_cookie('username')
        self.response.delete_cookie('password')
        self.redirect('/login')


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/signup', Signup),
                               ('/welcome', Welcome),
                               ('/login', Login),
                               ('/logout', Logout),
                               ('/newpost', NewPost),
                               ('/(\d+)', PermaLink),
                               ('/allposts', AllPosts),
                               ('/(\d+)/newcomment', NewComment),
                               ('/(\d+)/editcomment', EditComment),
                               ('/(\d+)/editpost', EditPost),
                               ('/(\d+)/deletepost', DeletePost),
                               ('/(\d+)/deletecomment', DeleteComment)
                               ], debug=True)

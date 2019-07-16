import os
import webapp2
import jinja2

from py.secure.secure import check_secure_val, make_secure_val
import py.blog.user as user


html_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(html_dir),
                               autoescape=True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))
        # can I do this: self.write(self.render_str(template, session, **kw)) ?

    def get_username_from_cookie(self):
        username_cookie = str(self.request.cookies.get('username'))
        return username_cookie and check_secure_val(username_cookie)

    def verify_username_cookie(self, uname):
        username_cookie = self.get_username_from_cookie()
        return username_cookie and check_secure_val(username_cookie) == uname

    def set_cookie(self, value, name):
        value_cookie = make_secure_val(str(value))
        self.response.headers.add_header('Set-Cookie', '%s=%s; Path=/'
                                         % (name, value_cookie))

    # create object of user to call methods on it later
    def current_user(self):
        return user.User.by_name(self.get_username_from_cookie())

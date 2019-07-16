import re
import webapp2

from ..secure.secure import hash_str, check_secure_val
from .user import User


class RegexValidator():
    # using re.compile() and saving the resulting regular expression object for
    #   reuse is more efficient when the expression will be used several times
    #       in a single program [https://docs.python.org/2/library/re.html]
    USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
    PASSWORD_RE = re.compile(r"^.{3,20}$")
    EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")

    def valid_username(self, username):
        """   "^[a-zA-Z0-9_-]{3,20}$
        if user name is correct this will return None which evaluates to false
        """
        if not self.USER_RE.match(username):
            return "That's not a valid username."
        # bool(match-object) returns True/False
        if User.by_name(username):
            return "Username already taken!"

    def valid_password(self, password):
        #   "^.{3,20}$"
        if not self.PASSWORD_RE.match(password):
            return "That wasn't a valid password."

    def valid_email(self, email):
        #   "^[\S]+@[\S]+.[\S]+$"
        if not self.EMAIL_RE.match(email) and email:
            return "That's not a valid email."


class SignupValidator(RegexValidator):
    """ put all errors -if any- into a dictionary
        input: params, see Signup().post_params
    """
    def errors(self, params):
        errors = {}
        for _, field in enumerate(params.keys()):
            method = "valid_{0}".format(field)
            # check if method is defined, call method from string: getattr
            if method in dir(self):
                errors[field] = getattr(self, method)(params[field]) or ''
        # check if password == verify
        if params['password'] != params['verify']:
            errors['verify'] = "Your passwords didn't match."
        return errors


class DBValidator(webapp2.RequestHandler):
    def valid_username(self, username):
        username_cookie = self.request.cookies.get('username')
        if username_cookie:
            if not check_secure_val(username_cookie) == username:
                return "Invalid login"
        else:
            return "Invalid login"

    def valid_password(self, password):
        crypt = hash_str(password)
        password_cookie = self.request.cookies.get('password')
        if password_cookie:
            if not password_cookie == crypt:
                return "Invalid login"


class LoginValidator(DBValidator):
    """ to check after the login, if login-cookie is correct
        THIS is NOT for the inital login, for that we have User.login()
        This method construction is overkill which is due to excercising
    """
    def errors(self, params):
        errors = {}
        for _, field in enumerate(params.keys()):
            method = "valid_{0}".format(field)
            if method in dir(self):
                errors[field] = getattr(self, method)(params[field]) or ''
        return errors

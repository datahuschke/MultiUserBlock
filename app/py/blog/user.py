"""
user.py defines the User and handles all functions which a User will use, which
currently are only like and comment

There are some classmethods for finding a User in the database and registering
a new one or handling the login-verification

This module depends on the secure module, which does the hashing as well as
hash validating

known problems/issus:
the like function stores a like in the database and directly after that updates
the total count of likes for the newly liked post in the Blogpost database.
The GAE's database is not consistent enought to read a value right after
storing it. using parent-keys makes it more consistent, but not consistent
enought. Therefore we force the function to sleep for 0.3 sec between writing
and reading from the databse. After writing there is another wait of 0.3 sec
because we want to render the page with the new like-count
"""
from google.appengine.ext import db
from time import sleep

from ..secure.secure import hash_str, valid_user_password
from .postlikes import Postlikes


def blogpost_key(group='default'):
    return db.Key.from_path('blogposts', group)


def users_key(group='default'):
    """
    https://cloud.google.com/appengine/docs/standard/python/datastore/keyclass:

    The following call creates a Key for an entity of kind Address with
    numeric ID 9876, under the parent key User/Boris:

    >>> k = db.Key.from_path('User', 'Boris', 'Address', 9876)

    An alternative way of creating the same Key is as follows:

    >>> p1 = db.Key.from_path('User', 'Boris')
    >>> k = db.Key.from_path('Address', 9876, parent=p1)

    PLUS this makes it more consistent:
    https://cloud.google.com/appengine/docs/standard/python/datastore/
                structuring_for_strong_consistency
    """
    return db.Key.from_path('users', group)


class User(db.Model):
    name = db.StringProperty(required=True)
    pw_hash = db.StringProperty(required=True)
    email = db.EmailProperty()

    @classmethod
    def get_id(cls, uid):
        return User.get_by_id(uid, parent=users_key())

    """ returns the user as query object, call by_name().name, _.pw_hash, ...
    cloud.google.com/appengine/docs/standard/python/datastore/queryclass
    """
    @classmethod
    def by_name(cls, name):
        return User.all().filter('name =', name).get()

    #creates a new User, still have to cast register().put() to store
    @classmethod
    def register(cls, name, pw, email=None):
        pw_hash = hash_str(pw)
        return User(parent=users_key(),
                    name=name,
                    pw_hash=pw_hash,
                    email=email)

    # check if user exists and pw is correct, then return username
    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_user_password(pw, u.pw_hash):
            return u.name

    def like(self, post):
        pl = Postlikes.all().filter('pid =', post.id()).filter('user =',
                                                               self.name).get()
        like_params = {}
        like_params['e_pid'] = post.id()
        if post.is_owner(self):
            like_params['e_msg'] = "You can't like your own post!"
            return like_params
        elif pl:
            like_params['e_msg'] = "You already like this post.."
            return like_params
        else:
            l = Postlikes(parent=blogpost_key(),
                          pid=post.id(), user=self.name)
            l.put()
            sleep(0.3)
            post.update_likes()
            sleep(0.3)

from google.appengine.ext import db


class Postlikes(db.Model):
    """ store who likes which posts
        pid = id of post, u = user
    """
    pid = db.IntegerProperty(required=True)
    user = db.StringProperty(required=True)

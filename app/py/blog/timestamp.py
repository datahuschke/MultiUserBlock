"""
With this class it is easy to create a new Timestamp for updating on in the
database via:
ts = TimeStamp.create()
"""
from google.appengine.ext import db


class TimeStamp(db.Model):
    timestamp = db.DateTimeProperty(auto_now_add=True)

    def id(self):
        return self.key().id()

    # test, if it is possible without .put() / .delete()
    @classmethod
    def create(cls):
        t = TimeStamp().put()
        ts = cls.get_by_id(t.id())
        ts.delete()
        return ts.timestamp

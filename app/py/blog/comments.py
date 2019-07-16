from google.appengine.ext import db
from time import sleep

from app.handler import Handler
from .timestamp import TimeStamp
import blogpost

global session


class Comments(db.Model):
    pid = db.IntegerProperty(required=True)
    user = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    lastupdate = db.DateTimeProperty(default=0)

    def id(self):
        return self.key().id()

        """

ToDo's
- maybe add some basic CSS / background images

        """

    @classmethod
    def create(cls, pid, user, content):
        return Comments(parent=blogpost.blogpost_key(),
                        pid=pid,
                        user=user,
                        content=content)


class NewComment(Handler):
    def get(self, pid):
        u = self.current_user()
        if not u:
            self.redirect("/login")
        else:
            p = blogpost.Blogpost.get_by_id(int(pid))
            self.render("newcomment.html", content=p, session=u.name,
                        like_params={}, comment={}, error="")

    def post(self, pid):
        u = self.current_user()
        content = self.request.get("comment_content")
        if content and u:
            post = blogpost.Blogpost.get_by_id(int(pid))
            Comments.create(int(post.id()), u.name, content).put()
            sleep(0.3)
            post.update_comments()
            sleep(0.3)
            self.redirect('/%d' % int(pid))
        elif not u:
            self.redirect('/login')
        else:
            error = "please actually write something ;)"
            p = blogpost.Blogpost.get_by_id(int(pid))
            self.render("newcomment.html", content=p, session=u.name,
                        like_params={}, comment={}, error=error)


class EditComment(Handler):
    def get(self, cid):
        u = self.current_user()
        c = Comments.get_by_id(int(cid), parent=blogpost.blogpost_key())
        if not u:
            self.redirect('/login')
        elif c.user == u.name:  # only allow to edit your own comment
            p = blogpost.Blogpost.get_by_id(int(c.pid))
            self.render("newcomment.html", content=p, session=u.name, error="",
                        like_params={}, comment=c, editing=int(c.pid))
        else:
            self.redirect('/%d' % int(c.pid))

    def post(self, cid):
        u = self.current_user()
        content = self.request.get("comment_content")
        c = Comments.get_by_id(int(cid), parent=blogpost.blogpost_key())
        if content and u.name:
            ts = TimeStamp.create()
            setattr(c, 'content', content)
            setattr(c, 'lastupdate', ts)
            c.put()
            sleep(0.1)  # the redirect is faster than the db update, so sleep
            self.redirect('/%d' % int(c.pid))
        elif not u:
            self.redirect('/login')
        else:
            error = "you didn't write anything!"
            p = blogpost.Blogpost.get_by_id(int(c.pid))
            self.render("newcomment.html", content=p, session=u.name,
                        like_params={}, comment="", error=error,
                        editing=int(c.pid))


class DeleteComment(Handler):
    def get(self, cid):
        params = self.get_params(cid)
        delete = {}
        delete['msg'] = "Do you really want to delete this comment:"
        delete['id'] = int(cid)
        self.render(params['url'], content=params['p'], delete=delete,
                    session=params['u'].name, comments=params['c'],
                    like_params={})

    def post(self, cid):
        params = self.get_params(cid)
        c = Comments.get_by_id(int(cid), parent=blogpost.blogpost_key())
        if not params['u']:
            self.redirect('/login')
        if self.request.get('delete') and params['u'].name == c.user:
            c.delete()
            sleep(0.1)
            self.redirect('/' + str(params['p'].id()))
        else:
            self.redirect('/' + str(params['p'].id()))

    def get_params(self, cid):
        params = {}
        params['u'] = self.current_user()
        pid = Comments.get_by_id(int(cid), parent=blogpost.blogpost_key()).pid
        params['p'] = blogpost.Blogpost.get_by_id(int(pid))
        params['c'] = Comments.all().filter('pid =', pid)
        params['url'] = "permalink.html"
        return params

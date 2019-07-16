from google.appengine.ext import db
from time import sleep

from app.handler import Handler
from .postlikes import Postlikes
from .timestamp import TimeStamp
import comments

global session


def blogpost_key(group='default'):
    return db.Key.from_path('blogposts', group)


class Blogpost(db.Model):
    """ 'likes' stores only the total amount of likes, e.g. 42.
        'comments' stores only the total amount of comments, e.g. 15 """
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    lastupdate = db.DateTimeProperty(default=0)
    # should be changed from username into userID
    user = db.StringProperty(required=True)
    likes = db.IntegerProperty(default=0)
    comments = db.IntegerProperty(default=0)

    def id(self):
        return int(self.key().id())

    def is_owner(self, user):
        return user.name == self.user

    def update_likes(self):
        l_count = Postlikes.all().filter('pid =', self.id()).count()
        setattr(self, 'likes', l_count)
        self.put()

    def update_comments(self):
        c_count = comments.Comments.all().filter('pid =', self.id()).count()
        setattr(self, 'comments', c_count)
        self.put()

    def delete_including_comments_and_likes(self):
        c = comments.Comments.all().filter('pid =', self.id())
        l = Postlikes.all().filter('pid =', self.id())
        if c and c.count() > 1:
            for comment in c.get():
                comment.delete()
        elif c and c.count() == 1:
            c.get().delete()
        if l and l.count() > 1:
            for like in l.get():
                like.delete()
        elif l and l.count() == 1:
            l.get().delete()
        self.delete()
        sleep(0.1)

    @classmethod
    def create(cls, subject, content, user):
        return Blogpost(subject=subject, content=content, user=user)


class NewPost(Handler):
    def get(self, subject="", content="", error=""):
        u = self.current_user()
        if u:
            self.render("newpost.html", subject=subject, content=content,
                        error=error, session=u.name)
        else:
            self.redirect("/login")

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")
        u = self.current_user()

        if subject and content and u:
            p = Blogpost.create(subject, content, u.name).put()
            self.redirect('/%d' % p.id())
        elif not u:
            self.redirect('/login')
        else:
            error = "please write both, a title and a blogpost!"
            self.render("newpost.html", subject=subject, content=content,
                        error=error, session=u.name)


class PermaLink(Handler):
    def get(self, pid):
        params = self.get_params(pid)
        self.render("permalink.html", content=params['p'], session=params['u'],
                    like_params={}, comments=params['c'])

    def post(self, pid):
        params = self.get_params(pid)
        if not params['u']:
            self.redirect('/login')
        else:
            like_params = self.current_user().like(params['p'])
            if not like_params:
                self.redirect('/' + str(pid))
            else:
                self.render("permalink.html", content=params['p'],
                            session=params['u'], like_params=like_params,
                            comments=params['c'])

    # I need exactly this again for DeletePost
    def get_params(self, pid):
        params = {}
        params['u'] = self.get_username_from_cookie()
        params['p'] = Blogpost.get_by_id(int(pid))
        params['c'] = comments.Comments.all().filter('pid =', params['p'].id())
        return params


class AllPosts(Handler):
    def get(self):
        query = "SELECT * FROM Blogpost ORDER BY created DESC"
        contents = db.GqlQuery(query)
        session = self.get_username_from_cookie()
        self.render("allposts.html", contents=contents,
                    session=session, like_params={})

    def post(self):
        pid = int(self.request.get("pid"))
        post = Blogpost.get_by_id(pid)
        u = self.current_user()
        print("\n TEST \n")
        print(u)
        print("\n TEST \n")
        if not u:
            self.redirect('/login')
        else:
            like_params = u.like(post)
            if not like_params:
                self.redirect('/allposts')
            else:
                query = "SELECT * FROM Blogpost ORDER BY created DESC"
                contents = db.GqlQuery(query)
                self.render("allposts.html", contents=contents,
                            session=u.name, like_params=like_params)


class EditPost(Handler):
    def get(self, pid):
        u = self.current_user()
        p = Blogpost.get_by_id(int(pid))
        if not u:
            self.redirect('/login')
        elif p.user == u.name:
            self.render("newpost.html", subject=p.subject, editing=int(pid),
                        content=p.content, error="", session=u.name)
        else:
            self.redirect('/%d' % int(pid))

    def post(self, pid):
        u = self.current_user()
        subject = self.request.get("subject")
        content = self.request.get("content")
        if subject and content and u:
            ts = TimeStamp.create()
            p = Blogpost.get_by_id(int(pid))
            setattr(p, 'subject', subject)
            setattr(p, 'content', content)
            setattr(p, 'lastupdate', ts)
            p.put()
            sleep(0.1)  # the redirect is faster than the db update
            self.redirect('/%d' % int(pid))
        elif not u:
            self.redirect('/login')
        else:
            error = "please write both, a title and a blogpost!"
            self.render("newpost.html", subject=subject, content=content,
                        error=error, session=u.name, editing=int(pid))


class DeletePost(PermaLink):
    def get(self, pid):
        params = self.get_params(pid)
        if not params['u'] or params['u'] != params['p'].user:
            self.redirect('/%d' % int(pid))
        else:
            self.render("deletepost.html", content=params['p'],
                        session=params['u'], like_params={},
                        comments=params['c'])

    def post(self, pid):
        u = self.current_user()
        p = Blogpost.get_by_id(int(pid))
        if not u:
            self.redirect('/login')
        if self.request.get('delete') and u.name == p.user:
            p.delete_including_comments_and_likes()
            self.redirect('/')
        else:
            self.redirect('/' + str(pid) + '/deletepost')

import os
import jinja2
import webapp2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class Redirect(webapp2.RequestHandler):
     def get(self):
         self.redirect("/blog")

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_post(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_post(template, **kw))

class Blog_Post(db.Model):
    title = db.StringProperty(required = True)
    article = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)


class MainHandler(Handler):
    def render_front(self, title="", article="", error=""):
        blogs = db.GqlQuery("SELECT * FROM Blog_Post "
                            "ORDER BY created DESC "
                            "LIMIT 5; ")

        self.render("blog.html", title=title, article=article, error=error, blogs=blogs)

    def get(self):
        self.render_front()

class ViewPostHandler(Handler):

    def get(self, the_id):
        b = int(the_id)
        b_id = Blog_Post.get_by_id(b)

        if b_id:
            self.render("singlepost.html", b_id=b_id)

        else:
            error = "There's nothing to see here!"
            self.response.out.write(error)
            return

class AddPostPage(Handler):

    def get(self):
        self.render("newpost.html")

    def post(self):
        title = self.request.get("title")
        article = self.request.get("article")

        if title and article:
            p = Blog_Post(title = title, article = article)
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "Please input a title AND text."
            self.render_front(title, article, error)

def get_posts(limit, offset):
    pass
    # TODO: query the database for posts, and return them

app = webapp2.WSGIApplication([
    ('/blog', MainHandler),
    ('/newpost', AddPostPage),
    webapp2.Route('/blog/<the_id:\d+>', ViewPostHandler),
], debug=True)
# https://github.com/indigoblow/build-a-blog.git

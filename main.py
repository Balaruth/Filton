#!/usr/bin/env python
import os
import jinja2
import webapp2
from models import Message


template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if params is None:
            params = {}
        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):
        return self.render_template("index.html")

    def post(self):
        gb_name = self.request.get("fullname")
        gb_email = self.request.get("email")
        gb_message = self.request.get("message")


        import re
        antiscript = re.findall("<(\w+)>", gb_name)
        antiscript2 = re.findall("<(\w+)>", gb_email)
        antiscript3 = re.findall("<(\w+)>", gb_message)
        if antiscript or antiscript2 or antiscript3:
            pass
        else:
            msg = Message(message_author=gb_name, message_email=gb_email, message_text=gb_message)
            msg.put()

        return self.redirect_to("posts")

class PostsHandler(BaseHandler):
    def get(self):
        messages = Message.query(Message.deleted == False).fetch()
        params = {"messages": messages}
        return self.render_template("posts.html", params=params)

app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler, name="main"),
    webapp2.Route('/posts', PostsHandler, name="posts"),
    webapp2.Route('/message/{{ message.key.id()', DetailHandler),
    webapp2.Route('/message/{{ message.key.id()/post_edit', EditHandler),
    webapp2.Route('/message/{{ message.key.id()/post_delete', DeleteHandler),
], debug=True)

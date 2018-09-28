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

        if not gb_name:
            gb_name = "Anonymous"

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

class DetailHandler(BaseHandler):
    def get(self, message_id):
        message = Message.get_by_id(int(message_id))
        params = {"message": message}
        return self.render_template("post_detail.html", params=params)

class EditHandler(BaseHandler):
    def get(self, message_id):
        message = Message.get_by_id(int(message_id))
        params = {"message": message}
        return self.render_template("post_edit.html", params=params)

    def post(self, message_id):
        new_text = self.request.get("message")
        message = Message.get_by_id(int(message_id))
        message.message_text = new_text
        message.put()
        return self.redirect_to("posts")

class DeleteHandler(BaseHandler):
    def get(self, message_id):
        message = Message.get_by_id(int(message_id))
        params = {"message": message}
        return self.render_template("post_delete.html", params=params)

    def post(self, message_id):
        message = Message.get_by_id(int(message_id))
        message.deleted = True
        message.put()
        return self.redirect_to("posts")

class GraveyardHandler(BaseHandler):
    def get(self):
        messages = Message.query(Message.deleted == True).fetch()
        params = {"messages": messages}
        return self.render_template("post_graveyard.html", params=params)

class GraveyardPermadeleteHandler(BaseHandler):
    def get(self, message_id):
        message = Message.get_by_id(int(message_id))
        params = {"message": message}
        return self.render_template("post_graveyard_perma_delete.html", params=params)

    def post(self, message_id):
        message = Message.get_by_id(int(message_id))
        message.key.delete()
        return self.redirect_to("graveyard")

class GraveyardRestoreHandler(BaseHandler):
    def get(self, message_id):
        message = Message.get_by_id(int(message_id))
        params = {"message": message}
        return self.render_template("post_graveyard_restore.html", params=params)

    def post(self, message_id):
        message = Message.get_by_id(int(message_id))
        message.deleted = False
        message.put()
        return self.redirect_to("graveyard")

app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/posts', PostsHandler, name="posts"),
    webapp2.Route('/message/<message_id:\d+>', DetailHandler),
    webapp2.Route('/message/<message_id:\d+>/post_edit', EditHandler),
    webapp2.Route('/message/<message_id:\d+>/post_delete', DeleteHandler),
    webapp2.Route('/post_graveyard', GraveyardHandler, name="graveyard"),
    webapp2.Route('/message/<message_id:\d+>/post_graveyard_perma_delete', GraveyardPermadeleteHandler),
    webapp2.Route('/message/<message_id:\d+>/post_graveyard_restore', GraveyardRestoreHandler),
], debug=True)

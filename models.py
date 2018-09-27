from google.appengine.ext import ndb

class Message(ndb.Model):
    message_text = ndb.StringProperty()
    message_author = ndb.StringProperty()
    message_email = ndb.StringProperty()
    deleted = ndb.BooleanProperty(default=False)
    created = ndb.DateTimeProperty(auto_now_add=True)
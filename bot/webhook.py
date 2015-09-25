from flask import request
from telegram import Update
from .text import Text
from .document import Document

class Webhook(object):
    types = {
            'text' : Text,
            'document' : Document,
            }

    def __init__(self):
        update = Update.de_json(request.get_json(force=True))
        if getattr(update, 'message', None):
            for t, c in self.types.items():
                if getattr(update.message, t):
                    m = c()
                    m.update = update
                    m.parse()
                    m.run()
                    m.respond()

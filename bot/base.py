from flask import current_app, request
from telegram import Bot, Update
import sys

class BotBase(object):
    text = None
    message_args = {}
    update = None
    chat_id = None
    user_id = None

    def __init__(self):
        self.bot = Bot(current_app.config.get('TOKEN'))

    def respond(self):
        if self.text:
            self.bot.sendMessage(self.update.message.chat.id, text = self.text, **self.message_args)

    def flush(self):
        sys.stdout.flush()

    def parse(self):
        self.chat_id = self.update.message.chat.id
        self.user_id = self.update.message.from_user.id

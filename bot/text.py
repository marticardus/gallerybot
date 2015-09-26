from flask import url_for
from models.user import User
from models.gallery import Gallery
from .base import BotBase

class Text(BotBase):
    def run(self):
        args = self.update.message.text.split(' ', 2)
        if args[0] == '/register':
            self.text = 'Username:'
            user = User().search(tgid = self.user_id)
            if not user:
                User(tgid = self.user_id).save()
                self.text = 'Complete register: https://telegram.me/ACSGalleryBot?start=%s' % self.user_id
            else:
                self.text = 'User added to gallery'
            # set gallery permission at this point because i have chat id
        elif args[0] == '/start':
            if len(args) > 1 and int(args[1]) == int(self.chat_id):
                self.text = 'Username:'
                self.message_args = { 'reply_markup' : { 'force_reply' : True } }

        elif getattr(self.update.message, 'reply_to_message'):
            if self.update.message.reply_to_message.text == 'Username:':
                user = User().search(tgid = self.user_id)
                if user:
                    user.setattr('username', self.update.message.text)
                    user.save()
                    self.text = 'Password:'
                    self.message_args = { 'reply_markup' : { 'force_reply' : True } }
                return 'ok'
            elif self.update.message.reply_to_message.text == 'Password:':
                user = User().search(tgid = self.user_id)
                user.setattr('password', self.update.message.text)
                user.save()
                self.text = 'User succesfuly registered'
        elif args[0] == '/create':
            if hasattr(self.update.message.chat, 'title'):
                gallery = Gallery().search(tgid = self.chat_id)
                if not gallery:
                    gallery = Gallery(tgid = self.chat_id, title = self.update.message.chat.title).save()
                self.text = 'Gallery URL: %s' % url_for('gallery', id = gallery.eid.value, _external = True, _scheme = 'https')
            else:
                self.text = 'Bot only works in groups'
        elif args[0] == '/remove':
            gallery = Gallery().search(tgid = self.chat_id)
            if gallery:
                gallery.delete()
                self.text = 'Gallery deleted'
            else:
                self.text = 'Gallery is not registered'
            # TODO: Confirm
        elif args[0] == '/settings':
            args.pop(0)
            gallery = Gallery().search(tgid = self.chat_id)
            if gallery:
                if len(args) == 0:
                    self.text = gallery.as_dict()
                elif len(args) == 1:
                    value = gallery.as_dict()
                    if getattr(gallery, args[0]):
                        self.text = getattr(gallery, args[0]).value
                    else:
                        self.text = 'Setting %s not found' % args[0]
                else:
                    value = ' '.join(args[1:])
                    gallery.setattr(args[0], value)
                    gallery.save()
                    self.text = 'Setting %s set to %s' % (args[0], value)
            else:
                self.text = 'Gallery is not registered'

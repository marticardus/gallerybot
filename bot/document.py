from flask import url_for
from models.gallery import Gallery
from models.file import File
from .base import BotBase
from common.utils import write_file, write_json, read_file, read_json, thumbnail
import os

class Document(BotBase):
    def run(self):
        gallery = Gallery().search(tgid = self.chat_id)
        if gallery:
            newfile = self.bot.getFile(self.update.message.document.file_id)
            file_name = self.update.message.document.file_id
            newfile.download(file_name)
            writed = False
            if os.path.exists(file_name):
                writed = write_file(file_name, read_file(file_name, storage = 'local', append_path = False), acl = 'public-read', mime_type = self.update.message.document.mime_type)
                thumbnail(file_name)
                os.remove(file_name)
                write_file('%s.json' % file_name, self.update.to_json())
            if writed:
                file_id = File(gallery_eid = gallery.eid.value, file_id = self.update.message.document.file_id)
                file_id.save()
                sendLink = getattr(gallery, 'sendLink', None)
                if sendLink and sendLink.value:
                    self.text = 'File URL: %s' % url_for('image', file_id = file_id.eid.value, _external = True, disable_web_page_preview = True)
            else:
                self.text = 'Failed to download file'
        else:
            self.text = 'Gallery does not exist, please create first'


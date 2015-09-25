from models.gallery import Gallery
from models.file import File
from .base import BotBase

class Document(BotBase):
    def __init__(self):
        super(Document, self).__init__()

    def run(self):
        gallery = Gallery().search(tgid = update.message.chat.id)
        if gallery:
            newfile = bot.getFile(update.message.document.file_id)
            file_name = update.message.document.file_id
            newfile.download(file_name)
            writed = False
            if os.path.exists(file_name):
                writed = write_file(file_name, read_file(file_name, storage = 'local', append_path = False), acl = 'public-read', mime_type = update.message.document.mime_type)
                thumbnail(file_name)
                os.remove(file_name)
                write_file('%s.json' % file_name, update.to_json())
            if writed:
                file_id = File(gallery_eid = gallery.eid, file_id = update.message.document.file_id)
                file_id.save()
                sendLink = getattr(gallery, 'sendLink', None)
                if sendLink == 'True':
                    self.text = 'File URL: %s' % url_for('image', file_id = file_id.eid, _external = True, disable_web_page_preview = True)
            else:
                self.text = 'Failed to download file'
        else:
            self.text = 'Gallery does not exist, please create first'


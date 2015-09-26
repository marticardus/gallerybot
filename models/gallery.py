from common.model import Model, Field
from models.file import File

class Gallery(Model):
    table = 'gallery'

    tgid = Field(type = int, required = True, hidden = True)
    sendLink = Field(type = bool, default = False)

    def __init__(self, **kwargs):
        super(Gallery, self).__init__(**kwargs)

    def delete(self):
        if getattr(self, 'eid', None):
            for f in File().filter( gallery_eid = self.eid.value ):
                f.delete()
        super(Gallery, self).delete()

from common.model import Model, Field
from common.utils import delete_file

class File(Model):
    table = 'file'

    gallery_eid = Field(type = int)

    def __init__(self, **kwargs):
        super(File, self).__init__(**kwargs)

    def delete(self):
        filename = getattr(self, 'file_id', None)
        if filename:
            delete_file(filename.value)
            delete_file('%s.json' % filename.value)
        super(File, self).delete()

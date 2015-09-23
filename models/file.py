from common.model import Model
from common.utils import delete_file

class File(Model):
    table = 'file'

    def __init__(self, **kwargs):
        super(File, self).__init__(**kwargs)

    def delete(self):
        filename = getattr(self, 'file_id', None)
        if filename:
            delete_file(filename)
            delete_file('%s.json' % filename)
        super(File, self).delete()

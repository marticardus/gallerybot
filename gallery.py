from utils import get_table
from tinydb import where
from tinydb.operations import delete

class Gallery(object):
    def __init__(self):
        self.db = get_table('gallery')

    def create(self, tgid, name):
        id = self.get(tgid)
        return id if id else self.db.insert({ 'tgid' : tgid, 'name' : name })

    def delete(self, tgid):
        row = self.db.get(where('tgid') == tgid)
        if row:
            self.db.remove(eids = [ row.eid ])

    def getid(self, id):
        return self.db.get(eid=id)

    def get(self, tgid):
        id = self.db.get(where('tgid') == tgid)
        if id:
            return id.eid
        return None
        

class File(object):
    def __init__(self):
        self.db = get_table('files')

    def add(self, gallery_id, file_id):
        id = self.get(file_id)
        return id if id else self.db.insert({ 'gallery_id' : gallery_id, 'file_id' : file_id })

    def get(self, file_id):
        row = self.db.get(where('file_id') == file_id)
        if row:
            return row.eid
        return False

    def get_all(self, gallery_id):
        rows = self.db.search(where('gallery_id') == gallery_id)
        return rows

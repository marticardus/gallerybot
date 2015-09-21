from utils import get_table
from tinydb import where
from tinydb.operations import delete
from flask import current_app
import os, json

class Gallery(object):
    def __init__(self):
        self.db = get_table('gallery')

    def create(self, tgid, name):
        id = self.get(tgid)
        return id if id else self.db.insert({ 'tgid' : tgid, 'name' : name })

    def delete(self, tgid):
        row = self.db.get(where('tgid') == tgid)
        if row:
            f = File()
            files = f.get_all(row.eid)
            for fd in files:
                f.delete(fd.eid)

    def getid(self, id):
        return self.db.get(eid=id)

    def get(self, tgid):
        id = self.db.get(where('tgid') == tgid)
        if id:
            return id.eid
        return None
        
    def config_get_value(self, tgid, var):
        gallery_id = self.get(tgid)
        if gallery_id:
            row = self.db.get(eid = gallery_id)
            if row and var in row:
                return row[var]
        return None

    def config(self, tgid, var = None, value = None):
        row = self.get(tgid)
        if row:
            gallery_id = row
        else:
            return 'Gallery not found'
        if var:
            if value:
                self.db.update({ var : value }, eids = [ gallery_id ])
                return '%s saved' % var
            else:
                row = self.db.get(eid = gallery_id)
                if row:
                    return 'Var %s = %s' % (var, row[var])
                else:
                    return 'Not found'
        else:
            row = self.db.get(eid = gallery_id)
            row.pop('tgid')
            return row

    def get_all(self):
        galleries = list()
        rows = self.db.all()
        for row in rows:
            public = row.get('public', True)
            if public == 'True' or public == True:
                galleries.append(row)
        return galleries

class File(object):
    def __init__(self):
        self.db = get_table('files')

    def delete(self, file_id):
        row = self.db.get(eid=file_id)
        if row:
            if os.path.exists(os.path.join(current_app.config.get('FILE_PATH'), row['file_id'])):
                os.remove(os.path.join(current_app.config.get('FILE_PATH'), row['file_id']))
            if os.path.exists(os.path.join(current_app.config.get('FILE_PATH'), '%s.json' % row['file_id'])):
                os.remove(os.path.join(current_app.config.get('FILE_PATH'), '%s.json' % row['file_id']))
            self.db.remove(eids = [ row.eid ])

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

    def getid(self, eid):
        f = self.db.get(eid = eid)
        if f:
            path = current_app.config.get('FILE_PATH')
            with open(os.path.join(path, '%s.json' % f['file_id']), 'r') as file_info:
                d = json.load(file_info)
                return d
        return False

from flask import current_app
from tinydb import TinyDB, where
from .tinydbs3 import S3Storage
import os
import copy

class Model(object):
    table = 'default'
    exclude_fields = [ 'db', 'table', 'submit' ]

    def __init__(self, **kwargs):
        table = os.path.join(current_app.config.get('DB_PATH', 'gallery_db'), '%s.json' % self.table)
        self.db = TinyDB(table, storage = S3Storage)
        self.eid = None

        for key, value in kwargs.items():
            setattr(self, key, value)

    def all(self):
        rows = list()
        for row in self.db.all():
            rows.append( self.as_obj(row) )
        return rows

    def filter(self, **kwargs):
        rows = list()
        eids = list()
        for field, value in kwargs.iteritems():
            founds = self.db.search(where(field) == value)
            for found in founds if founds else []:
                if found.eid not in eids:
                    eids.append(found.eid)
                    rows.append( self.as_obj(found) )
        return rows

    def get(self, eid):
        row = self.db.get(eid = eid)
        if row:
            return self.as_obj(row)
        return False

    def search(self, **kwargs):
        for field, value in kwargs.iteritems():
            row = self.db.search(where(field) == value)
            if row:
                if type(row) == list:
                    row = row[0]
                return self.as_obj(row)
        return False

    def create(self):
        insert = self.as_dict()
        return self.db.insert(insert)

    def update(self):
        update = self.as_dict()
        return self.db.update(update, eids = [ self.eid ])

    def save(self):
        if self.eid:
            self.eid = int(self.eid)
            return self.update()
        else:
            create = self.create()
            self.eid = create
            return self

    def delete(self):
        self.db.remove( eids = [ self.eid ] )

    def as_dict(self):
        args = dict()
        for key in self.__dict__.keys():
            if key not in self.exclude_fields:
                if getattr(self, key):
                    args[key] = getattr(self, key)
        return args

    def clean(self):
        for key in self.__dict__.keys():
            if key not in self.exclude_fields:
                delattr(self, key)

    def as_obj(self, row):
        self.clean()
        self.eid = row.eid
        for key, value in row.items():
            setattr(self, key, value)
        return copy.copy( self )

    def from_form(self, form):
        for key, value in form.items():
            setattr(self, key, value)
        return self

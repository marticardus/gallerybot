from flask import current_app
from tinydb import TinyDB, where
import os
import copy

class Model(object):
    table = 'default'
    exclude_fields = [ 'db', 'table' ]

    def __init__(self, **kwargs):
        table = os.path.join(current_app.config.get('DB_DIR', '/tmp'), '%s.json' % self.table)
        self.db = TinyDB(table)
        self.eid = None

        for key, value in kwargs:
            setattr(self, key, value)

    def all(self):
        rows = list()
        for row in self.db.all():
            rows.append( self.as_obj(row) )
        return rows

    def get(self, eid):
        row = self.db.get(eid = eid)
        if row:
            return self.as_obj(row)
        return False

    def search(self, field, value):
        row = self.db.search(where(field) == value)
        if row:
            return self.as_obj(row)
        return False

    def create(self):
        insert = self.args_to_dict()
        return self.db.insert(insert)

    def update(self):
        update = self.args_to_dict()
        return self.db.update(update, eids = [ self.eid ])

    def save(self):
        if self.eid:
            return self.update()
        else:
            return self.create()

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

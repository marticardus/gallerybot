from flask import current_app
from tinydb import TinyDB, where
from .tinydbs3 import S3Storage
import os
import copy

class Field(object):
    def __init__(self, value = None, type = str, default = None, required = False, primary = False):
        self.type = type
        self.default = default
        self.required = required
        self.value = value
    
    def validate(self):
        valid = False
        if hasattr(self, 'value'):
            if self.required: valid = True
            try:
                self.value = getattr(self, 'type')(self.value)
                valid = True
            except:
                valid = False
        return valid

class Model(object):
    table = 'default'
    _exclude_fields = [ 'eid', 'db', 'table', 'submit', '_exclude_fields', 'exclude_fields' ]

    def __init__(self, **kwargs):
        table = os.path.join(current_app.config.get('DB_PATH', 'gallery_db'), '%s.json' % self.table)
        self.db = TinyDB(table, storage = S3Storage)
        self.eid = Field(type = int, required = False, primary = False)

        for key, value in kwargs.items():
            self.setattr(key, value)

        exclude_fields = getattr(self, 'exclude_fields', None)
        if exclude_fields:
            self._exclude_fields += exclude_fields

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
        return self.db.update(update, eids = [ self.eid.value ])

    def save(self):
        if self.eid.value:
            self.eid.validate()
            return self.update()
        else:
            create = self.create()
            self.eid.value = create
            return self

    def delete(self):
        self.db.remove( eids = [ self.eid.value ] )

    def as_dict(self):
        args = dict()
        for key in self.__dict__.keys():
            if key not in self._exclude_fields:
                attr = getattr(self, key, None)
                if attr:
                    if attr.validate():
                        args[key] = attr.value
        return args

    def clean(self):
        for key in self.__dict__.keys():
            if key not in self._exclude_fields:
                delattr(self, key)

    def as_obj(self, row):
        self.clean()
        if not getattr(self, 'eid', None):
            self.eid = Field(value = row.eid, type = int, required = False, primary = False)
        for key, value in row.items():
            self.setattr(key, value)
        return copy.copy( self )

    def setattr(self, key, value):
        attr = getattr(self, key, Field())
        if type(attr) != Field:
            attr = Field()
        attr.value = value
        setattr(self, key, attr)

    def from_form(self, form):
        for key, value in form.items():
            self.setattr(key, value)
        return self

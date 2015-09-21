from flask import current_app
from utils import get_table
from tinydb import where

class User(object):
    def __init__(self, tgid, username = None, password = None):
        self.db = get_table('users')
        self.tgid = tgid
        self.username = username
        self.password = password

        user = self.db.get(where('tgid') == tgid)
        if user:
            self.user_id = user.eid
        else:
            self.create()

    def get(self, username = None):
        if not username:
            username = self.username
        if not self.username:
            return False

        user = self.db.search(where('username') == username)
        if user:
            return user
        return False

    def create(self):
        insert = self.args_to_dict()
        insert['tgid'] = self.tgid
        return self.db.insert(insert)

    def save(self):
        update = self.args_to_dict()
        self.db.update(update, eids = [ self.user_id ])

    def args_to_dict(self):
        args = dict()
        for key in [ 'username', 'password' ]:
            if getattr(self, key):
                args[key] = getattr(self, key)
        return args

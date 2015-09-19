import string, random, os
from flask import current_app
from tinydb import TinyDB

def get_table(table):
    db = os.path.join(current_app.config.get('DB_DIR'), '%s.json' % table)
    return TinyDB(db)

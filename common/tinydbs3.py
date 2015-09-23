from boto.s3.connection import S3Connection
from boto.s3.key import Key
from tinydb.storages import Storage
from flask import current_app
import json

class S3Storage(Storage):
    def __init__(self, filename):
        self.filename = filename

    def read(self):
        self._get_key()
        if self.key and self.key.exists():
            return json.loads(self.key.get_contents_as_string())
        else:
            return {}

    def write(self, data):
        self._get_key()
        if self.key:
            self.key.set_contents_from_string(json.dumps(data))
        else:
            return False

    def _connect(self):
        self.con = S3Connection(
                aws_access_key_id = current_app.config['S3_ACCESS_KEY'],
                aws_secret_access_key = current_app.config['S3_SECRET_KEY'],
                is_secure = False,
                host = current_app.config['S3_SERVER']
                )

    def _get_bucket(self):
        self._connect()
        self.bucket = self.con.get_bucket(current_app.config.get('S3_BUCKET'))
        if not self.bucket:
            self.bucket = self.con.create_bucket(current_app.config.get('S3_BUCKET'))

    def _get_key(self):
        self._get_bucket()
        key = Key(self.bucket)
        key.name = self.filename
        key.content_type = 'application/json'

        self.key = key

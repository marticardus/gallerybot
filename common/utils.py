import string, random, os, json
from flask import current_app
from boto.s3.connection import S3Connection
from boto.s3.key import Key

def s3_key(filename):
    con = S3Connection(
            aws_access_key_id = current_app.config['S3_ACCESS_KEY'],
            aws_secret_access_key = current_app.config['S3_SECRET_KEY'],
            is_secure = False,
            host = current_app.config['S3_SERVER']
            )

    bucket = con.get_bucket(current_app.config.get('S3_BUCKET'))
    if not bucket:
        bucket = con.create_bucket(current_app.config.get('S3_BUCKET'))

    key = Key(bucket)
    key.name = filename
    return key

def delete_file(filename, storage = None, append_path = True):
    if not storage:
        storage = current_app.config.get('STORAGE', 'local')
    if storage == 'local':
        if append_path:
            filename = os.path.join(current_app.config.get('MEDIA_FOLDER'), filename)
        os.remove(filename)
    elif storage == 's3':
        if append_path:
            filename = '/'.join([ current_app.config.get('MEDIA_FOLDER', 'media'), filename ])
        key = s3_key(filename)
        if key.exists():
            key.delete()

def write_file(filename, data, storage = None, append_path = True, acl = 'private', mime_type = None):
    if not storage:
        storage = current_app.config.get('STORAGE', 'local')
    write_status = True
    if storage == 'local':
        if append_path:
            filename = os.path.join(current_app.config.get('MEDIA_FOLDER'), filename)
        with open(filename, 'w') as fd:
            fd.write(data)
    elif storage == 's3':
        if append_path:
            filename = '/'.join([ current_app.config.get('MEDIA_FOLDER', 'media'), filename ])
        key = s3_key(filename)
        if mime_type:
            key.content_type = mime_type
        key.set_contents_from_string(data)
        key.set_acl(acl)

    return write_status

def read_file(filename, storage = None, append_path = True):
    if not storage:
        storage = current_app.config.get('STORAGE', 'local')
    write_status = True
    if storage == 'local':
        if append_path:
            filename = os.path.join(current_app.config.get('MEDIA_FOLDER'), filename)
        with open(filename, 'r') as fd:
            data = fd.read()
    elif storage == 's3':
        if append_path:
            filename = '/'.join([ current_app.config.get('MEDIA_FOLDER', 'media'), filename ])
        key = s3_key(filename)
        data = key.get_contents_as_string()
    return data

def write_json(filename, data):
    return write_file(filename, json.dumps(data))

def read_json(filename):
    return json.loads(read_file(filename))

def thumbnail(filename, width = 200, height = 200):
    from PIL import Image
    from io import BytesIO
    im = Image.open(filename)
    im.thumbnail(( width, height ))
    temp_file = BytesIO()
    im.save(temp_file, im.format)
    filename = '%s_%sx%s' % (filename, width, height)
    write_file(filename, temp_file.getvalue(), acl = 'public-read')

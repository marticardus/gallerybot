# -*- coding: utf-8 -*-
# System
import os

# 3rd party
from flask import Flask, request, url_for, send_file, send_from_directory, redirect, abort
from telegram import Bot, Update

# Custom
from models.user import User
from models.file import File
from models.gallery import Gallery
from common.menu import MenuClass
from common.utils import read_json
from bot import Webhook

app = Flask(__name__)
app.config.from_object('config.Config')
menu = MenuClass()

@app.route('/echo/<string:text>')
def echo(text):
    return text

@menu.add('Users', '/users')
@app.route('/users', defaults = { 'eid' : None }, methods = [ 'GET', 'POST' ])
@app.route('/users/<int:eid>', methods = [ 'GET', 'POST' ])
def users(eid):
    if eid:
        if request.method == 'POST':
            user = User(eid = eid).from_form(request.form)
            user.save()
        else:
            user = User().get(eid = eid)
        return menu.render('form.html', form = user.as_form())
    else:
        return menu.render('list.html', items = User().all())

@app.route('/gallery/<int:id>/edit', methods = [ 'GET', 'POST' ])
def gallery_edit(id):
    if request.method == 'POST':
        gallery = Gallery(eid = id).from_form(request.form)
        gallery.save()
    else:
        gallery = Gallery().get(id)
        if gallery:
            return menu.render('form.html', form = gallery.as_form())
        else:
            abort(404)

@app.route('/gallery/<int:id>')
def gallery(id):
    gallery = Gallery().get(id)
    if gallery:
        files = File().filter( gallery_eid = gallery.eid )
        return menu.render('gallery.html', gallery = gallery, files = files)
    abort(404)

@app.route('/media/<string:filename>')
def media_file(filename):
    return send_from_directory(app.config['MEDIA_THUMBNAIL_FOLDER'], filename)

@app.route('/image/<int:file_id>', endpoint = 'image')
@app.route('/thumb/<int:file_id>', endpoint = 'thumb')
def image(file_id):
    thumb = True if '/thumb/' in request.url_rule.rule else False
    file_obj = File().get(file_id)
    info = read_json('%s.json' % file_obj.file_id)
    storage = app.config.get('STORAGE', 'local')
    if storage == 'local':
        return send_file(os.path.join(app.config.get('FILE_PATH'), info['message']['document']['file_id']), 
            mimetype = info['message']['document'].get('mime_type', 'text/plain'), 
            attachment_filename = info['message']['document']['file_name'])
    elif storage == 's3':
        scheme = 'http'
        filename = '/'.join([ app.config.get('MEDIA_FOLDER', 'media'), info['message']['document']['file_id'] ])
        if thumb: filename = '%s_200x200' % filename
        return redirect('%s://%s.%s/%s' % (scheme, app.config.get('S3_BUCKET'), app.config.get('S3_SERVER'), filename))

@menu.add('Index', '/')
@app.route('/')
def index():
    return menu.render('index.html', galleries = Gallery().all())

@app.route('/%s' % app.config.get('WEBHOOK_ROUTE'), methods=['POST'])
def telegramWebHook():
    Webhook()
    return ""

if __name__ == '__main__':
    bot = Bot(app.config.get('TOKEN'))
    #bot.setWebhook('https://%s/%s' % (app.config.get('WEBHOOK_HOST'), app.config.get('WEBHOOK_ROUTE')))
    app.run(host='0.0.0.0')

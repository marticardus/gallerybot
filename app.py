# -*- coding: utf-8 -*-
# System
import os, json
import shutil

# 3rd party
from flask import Flask, request, url_for, send_file, send_from_directory, jsonify, redirect
from telegram import Bot, Update

# Custom
from models.user import User
from models.file import File
from models.gallery import Gallery
from common.menu import MenuClass
from common.utils import read_file, read_json, write_file, write_json

app = Flask(__name__)
app.config.from_object('config.Config')
menu = MenuClass()

@menu.add('Users', '/users')
@app.route('/users', defaults = { 'eid' : None }, methods = [ 'GET', 'POST' ])
@app.route('/users/add', defaults = { 'eid' : 0 }, methods = [ 'GET', 'POST' ])
@app.route('/users/<int:eid>', methods = [ 'GET', 'POST' ])
def users(eid):
    if eid:
        if eid == 0:
            return menu.render('form.html', form = { 'username' : 'username', 'password' : 'password'} )
        else:
            return menu.render('form.html', form = User().get(eid = eid).as_dict())
    else:
        return menu.render('list.html', items = User().all())

@app.route('/gallery/<int:id>/edit', methods = [ 'GET', 'POST' ])
def gallery_edit(id):
    if request.method == 'POST':
        gallery = Gallery().from_form(request.form)
        gallery.save()
    else:
        gallery = Gallery().get(id)
    return menu.render('form.html', form = gallery.as_dict())

@app.route('/gallery/<int:id>')
def gallery(id):
    gallery = Gallery().get(id)
    files = File().filter( gallery_eid = gallery.eid )
    return menu.render('gallery.html', gallery = gallery, files = files)

@app.route('/media/<string:filename>')
def media_file(filename):
    return send_from_directory(app.config['MEDIA_THUMBNAIL_FOLDER'], filename)

@app.route('/image/<int:file_id>')
def image(file_id):
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
        return redirect('%s://%s.%s/%s' % (scheme, app.config.get('S3_BUCKET'), app.config.get('S3_SERVER'), filename))

@menu.add('Index', '/')
@app.route('/')
def index():
    return menu.render('index.html', galleries = Gallery().all())

@app.route('/%s' % app.config.get('WEBHOOK_ROUTE'), methods=['POST'])
def telegramWebHook():
    update = Update.de_json(request.get_json(force=True))
    text = None
    if getattr(update.message, 'document'):
        gallery = Gallery().search(tgid = update.message.chat.id)
        if gallery:
            newfile = bot.getFile(update.message.document.file_id)
            file_name = update.message.document.file_id
            newfile.download(file_name)
            writed = False
            if os.path.exists(file_name):
                writed = write_file(file_name, read_file(file_name, storage = 'local', append_path = False), acl = 'public-read', mime_type = update.message.document.mime_type)
                os.remove(file_name)
                write_file('%s.json' % file_name, update.to_json())
            if writed:
                file_id = File(gallery_eid = gallery.eid, file_id = update.message.document.file_id)
                file_id.save()
                sendLink = getattr(gallery, 'sendLink', None)
                if sendLink == 'True':
                    text = 'File URL: %s' % url_for('image', file_id = file_id.eid, _external = True, disable_web_page_preview = True)
            else:
                text = 'Failed to download file'
        else:
            text = 'Gallery does not exist, please create first'
        pass
    if getattr(update.message, 'text'):
        args = update.message.text.split(' ', 2)
        print update.message
        if args[0] == '/register':
            text = 'Username:'
            user = User().search(tgid = update.message.from_user.id)
            if not user:
                User(tgid = update.message.from_user.id).save()
                text = 'Complete register: https://telegram.me/ACSGalleryBot?start=%s' % update.message.from_user.id
            else:
                text = 'User added to gallery'
            # set gallery permission at this point because i have chat id
        elif args[0] == '/start':
            if int(args[1]) == int(update.message.chat.id):
                text = 'Username:'
                bot.sendMessage(update.message.from_user.id, text, reply_markup = { 'force_reply' : True })
            else:
                text = update.to_json()

        elif getattr(update.message, 'reply_to_message'):
            if update.message.reply_to_message.text == 'Username:':
                user = User().search(tgid = update.message.chat.id)
                user.username = update.message.text
                user.save()
                bot.sendMessage(update.message.chat.id, 'Password:', reply_markup = { 'force_reply' : True })
                return 'ok'
            elif update.message.reply_to_message.text == 'Password:':
                user = User().search(tgid = update.message.chat.id)
                user.password = update.message.text
                user.save()
                text = 'User succesfuly registered'
        elif args[0] == '/create':
            if hasattr(update.message.chat, 'title'):
                gallery = Gallery().search(tgid = update.message.chat.id)
                if not gallery:
                    gallery = Gallery(tgid = update.message.chat.id, title = update.message.chat.title).save()
                text = 'Gallery URL: %s' % url_for('gallery', id = gallery.eid, _external = True, _scheme = 'https')
            else:
                text = 'Bot only works in groups'
        elif args[0] == '/remove':
            gallery = Gallery().search(tgid = update.message.chat.id)
            if gallery:
                gallery.delete()
                text = 'Gallery deleted'
            else:
                text = 'Gallery is not registered'
            # TODO: Confirm
        elif args[0] == '/config':
            args.pop(0)
            gallery = Gallery.search(tgid = update.message.chat.id)
            if gallery:
                if len(args) == 0:
                    text = g.config(update.message.chat.id)
                elif len(args) == 1:
                    text = 'get one'
                    text = g.config(update.message.chat.id, args[0])
                else:
                    text = g.config(update.message.chat.id, args[0], args[1])
            else:
                text = 'Gallery is not registered'
        #else:
        #    text = update.to_json()
    if text:
        bot.sendMessage(update.message.chat.id, text, disable_web_page_preview=True)
    return ""

if __name__ == '__main__':
    bot = Bot(app.config.get('TOKEN'))
    bot.setWebhook('https://%s/%s' % (app.config.get('WEBHOOK_HOST'), app.config.get('WEBHOOK_ROUTE')))
    app.run(host='0.0.0.0')

# -*- coding: utf-8 -*-
import os, json
import shutil
from flask import Flask, request, url_for, send_file, send_from_directory
from telegram import Bot, Update
from utils import get_table
from gallery import Gallery, File
from menu import MenuClass
from flask.ext.thumbnails import Thumbnail

app = Flask(__name__)
app.config.from_object('config.Config')
menu = MenuClass()
thumb = Thumbnail(app)

@app.route('/gallery/<int:id>')
def gallery(id):
    f = File()
    g = Gallery()
    gallery = g.getid(id)
    files = f.get_all(id)
    return menu.render('gallery.html', gallery = gallery, files = files)

@app.route('/media/<string:filename>')
def media_file(filename):
    return send_from_directory(app.config['MEDIA_THUMBNAIL_FOLDER'], filename)

@app.route('/image/<int:file_id>')
def image(file_id):
    f = File()
    info = f.getid(file_id)
    return send_file(os.path.join(app.config.get('FILE_PATH'), info['message']['document']['file_id']), 
            mimetype = info['message']['document'].get('mime_type', 'text/plain'), 
            attachment_filename = info['message']['document']['file_name'])

@menu.add('Index', '/')
@app.route('/')
def index():
    db = get_table('gallery')
    return menu.render('index.html', galleries = db.all())

@app.route('/%s' % app.config.get('WEBHOOK_ROUTE'), methods=['POST'])
def telegramWebHook():
    g = Gallery()
    f = File()
    update = Update.de_json(request.get_json(force=True))
    text = None
    if getattr(update.message, 'document'):
        g_id = g.get(update.message.chat.id)
        if g_id:
            newfile = bot.getFile(update.message.document.file_id)
            file_name = update.message.document.file_id
            dest_file = os.path.join(app.config.get('FILE_PATH'), file_name)
            newfile.download(file_name)
            if os.path.exists(file_name):
                shutil.move(file_name, dest_file)
                with open('%s.json' % dest_file, 'w') as fileinfo:
                    fileinfo.write(update.to_json())
                    fileinfo.close()
            if os.path.exists(dest_file):
                file_id = f.add(g.get(update.message.chat.id), update.message.document.file_id)
                text = 'File URL: %s' % url_for('image', file_id = file_id, _external = True, disable_web_page_preview = True)
            else:
                text = 'Failed to download file'
        else:
            text = 'Gallery does not exist, please create first'
        pass
    if getattr(update.message, 'text'):
        args = update.message.text.split(' ')
        if args[0] == '/create':
            if hasattr(update.message.chat, 'title'):
                eid = g.create(update.message.chat.id, update.message.chat.title)
                text = 'Gallery URL: %s' % url_for('gallery', id = eid, _external = True, _scheme = 'https')
            else:
                text = 'Bot only works in groups'
        if args[0] == '/remove':
            g.delete(update.message.chat.id)
            # TODO: Confirm
            text = 'Gallery deleted'
        if args[0] == '/config':
            args.pop(0)
            if len(args) == 0:
                text = 'totes'
            elif len(args) == 1:
                text = 'get one'
            else:
                text = 'config var'
    if text:
        bot.sendMessage(update.message.chat.id, text, disable_web_page_preview=True)
    return ""

if __name__ == '__main__':
    bot = Bot(app.config.get('TOKEN'))
    bot.setWebhook('https://%s/%s' % (app.config.get('WEBHOOK_HOST'), app.config.get('WEBHOOK_ROUTE')))
    app.run(host='0.0.0.0')

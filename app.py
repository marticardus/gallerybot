# -*- coding: utf-8 -*-
import os, json
from flask import Flask, request, url_for
from telegram import Bot
from utils import get_table
from gallery import Gallery, File
from menu import MenuClass

app = Flask(__name__)
menu = MenuClass()
app.config.from_object('config.Config')


@app.route('/gallery/<int:id>')
def gallery(id):
    f = File()
    g = Gallery()
    gallery = g.getid(id)
    files = f.get_all(id)
    return menu.render('gallery.html', gallery = gallery, files = files)

@app.route('/image/<int:file_id>')
def image(file_id):
    pass

@menu.add('Index', '/')
@app.route('/')
def index():
    db = get_table('gallery')
    return menu.render('index.html', galleries = db.all())

@app.route('/%s' % app.config.get('WEBHOOK_ROUTE'), methods=['POST'])
def telegramWebHook():
    g = Gallery()
    f = File()
    data = request.json['message']
    text = None
    if 'document' in data:
        id = g.get(data['chat']['id'])
        if id:
            upload = bot.download(data)
            if upload:
                file_id = f.add(g.get(data['chat']['id']), upload)
                return url_for('image', file_id = file_id, _external = True)
                pass
            else:
                text = 'Failed to download file'
        else:
            text = 'Gallery does not exist, please create first'
        pass
    if 'text' in data:
        args = data['text'].split(' ')
        if args[0] == '/create':
            eid = g.create(data['chat']['id'], data['chat']['title'])
            text = 'Gallery URL: %s' % url_for('gallery', id = eid, _external = True)
        if args[0] == '/remove':
            g.delete(data['chat']['id'])
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
        bot.sendMessage(data['chat']['id'], text)
    return ""


if __name__ == '__main__':
    bot = Bot(app.config.get('TOKEN'))
    bot.setWebhook('https://%s/%s' % (app.config.get('WEBHOOK_HOST'), app.config.get('WEBHOOK_ROUTE')))
    bot.set('file_path', app.config.get('FILE_PATH'))
    app.run(host='0.0.0.0')

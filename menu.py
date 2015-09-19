from functools import wraps
from flask import render_template, request

class MenuClass(object):
    def __init__(self):
        self.menu = list()

    def add(self, name, url, order = None):
        item = { 'name' : name, 'url' : url }
        self.menu.append(item)
        def decorator(method):
            return method
        return decorator

    def make(self):
        return self.menu

    def render(self, template, **kwargs):
        return render_template(template, endpoint = request.endpoint, menu = self.make(), **kwargs)

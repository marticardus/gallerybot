from model import Model

class User(Model):
    table = 'users'

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

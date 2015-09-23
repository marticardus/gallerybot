from common.model import Model

class User(Model):
    table = 'user'

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

from common.model import Model, Field

class User(Model):
    table = 'user'

    tgid = Field(type = int, required = True)
    username = Field()
    password = Field()

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

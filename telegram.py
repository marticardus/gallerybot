import requests, os, json

class Bot(object):
    def __init__(self, token):
        self.token = token
        self.url = 'https://api.telegram.org/bot%s' % self.token
        self.file_url = 'https://api.telegram.org/file/bot%s' % self.token

    def set(self, var, value):
        setattr(self, var, value)

    def send(self, method, **kwargs):
        return requests.post('%s/%s' % (self.url, method), json=kwargs).json()

    def setWebhook(self, url):
        return self.send('setWebhook', url = url)

    def sendMessage(self, chat_id, text):
        return self.send('sendMessage', chat_id = chat_id, text = text)

    def getFile(self, file_id):
        return self.send('getFile', file_id = file_id)

    def download(self, request):
        if hasattr(self, 'file_path'):
            file_id = request['document']['file_id']
            file_info = self.getFile(file_id)
            path = file_info['result']['file_path']
            with open(os.path.join(self.file_path, '%s.json' % file_id), 'wb') as handle:
                handle.write(json.dumps(request))
                handle.close()
            with open(os.path.join(self.file_path, file_id), 'wb') as handle:
                response = requests.get('%s/%s' % (self.file_url, path), stream = True)
            
                for block in response.iter_content(1024):
                    handle.write(block)
                handle.close()
            return file_id
        return False

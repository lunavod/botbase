from Api import Api
from commands import aliases
import time
from datetime import datetime
import threading
import pickle

class Bot():

    def __init__(self, config):
        self.config = config
        self.max_id = 0
        self.api = Api(self.config)
        self.is_running = False

    def _parser(self, s):
        trigger = '%' + self.config.login
        args = []
        s = s.replace('<br/>\r', '\n')
        if s.count(trigger):
            l = s.split('\n')
            for i in l:
                raw = i[i.find(trigger) + len(trigger) + 1:]
                if raw != '':
                    args.append(raw.split(' '))
            return args

    def _handle(self, c, args):
        if args[0] in aliases:
            result = str(aliases[args[0]](self.api, c, args[1:]))
            self.api.comment(c.post_id, result, c.id)

    def run(self):
        self.is_running = True
        thread = threading.Thread(target=self.main, args=())
        thread.daemon = True
        thread.start()

    def main(self):
        while self.is_running:
            comments = self.api.get_stream()
            for comment_id in sorted(comments.keys()):
                cur = comments[comment_id]
                if cur.id > self.max_id:
                    self.max_id = cur.id
                    print(cur.body)
                    commands = self._parser(cur.body)
                    print(commands)
                    if commands and len(commands):
                        for i in commands:
                            thread = threading.Thread(target=self._handle, args=(cur, i))
                            thread.daemon = True
                            thread.start()
            time.sleep(2)

    def stop(self):
        print('STOPPING')
        self.is_running = False
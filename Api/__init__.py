from . import tabun_api as t_api
from . import bunker_api as b_api
from . import utils
from datetime import datetime

class Api():

    def __init__(self, config):
        self.config = config
        self._login()

    def _login(self):
        if self.config.site == 'tabun':
            self.User = t_api.User(login=self.config.login, passwd=self.config.password)
            self.User.timeout = 60
            print(self.User)
        elif self.config.site == 'bunker':
            self.User = b_api.User(login=self.config.login, password=self.config.password)
            print(self.User)

    def get_stream(self):
        if self.config.site == 'tabun':
            s = self.User.get_comments("/comments/")
            return utils.transform_comments_list(s, 'tabun')
        elif self.config.site == 'bunker':
            s = self.User.get_stream(comments='full')
            return utils.transform_comments_list(s, 'bunker')

    def comment(self, target_id, body, reply, type='blog'):
        body = utils.add_antispam(body)
        if self.config.site == 'tabun':
            c = self.User.comment(target_id, body, reply, type)
        elif self.config.site == 'bunker':
            c = self.User.add_comment(target_id, body, reply, type)
        return c

    def get_comments_from_post(self, id):
        if self.config.site == 'bunker':
            p = self.User.get_post(id, 'full')
            print(p['comments'])
            return utils.transform_comments_list(p['comments'], 'bunker')
        elif self.config.site == 'tabun':
            p = self.User.get_comments('/blog/'+str(id)+'.html')
            return utils.transform_comments_list(p, 'tabun')
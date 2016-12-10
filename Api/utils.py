from . import tabun_api as t_api
from datetime import datetime

class Comment():
    def __init__(self, time, post_id, id, body, author, vote_total):
        self.time = time
        self.post_id = post_id
        self.id = int(id)
        self.body = body
        self.author = author
        self.vote_total = int(vote_total)


def transform_comment(comment, type):
    if type == 'bunker':
        c = Comment(comment['date'], comment['targetId'], comment['id'], comment['text'], comment['author'][1], comment['rating'])
        return c
    elif type == 'tabun':
        body = t_api.utils.HTMLFormatter().format(comment.body)
        c = Comment(comment.time, comment.post_id, comment.comment_id, body, comment.author, comment.vote_total)
        return c

def transform_comments_list(l, type):
    new = {}
    for i in list(l.values()):
        c = transform_comment(i, type)
        new[c.id] = c
    return new

def add_antispam(s):
    antispam = '<span class="spoiler-body">%s</span>%s'%(
        datetime.strftime(datetime.now(), '%a %b %d %H:%M:%S %Y'),
        s
    )
    return antispam

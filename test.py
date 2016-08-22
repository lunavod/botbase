"""
from bot import Bot

test = Bot()
test.run()
input()
test.stop()
input()
"""

from Api import Api
from config import Config
import math

class StatItem():
    def __init__(self, count, plus, minus, user):
        self.user = user
        self.count = count
        self.plus = int(plus)
        self.minus = int(minus)

    def __repr__(self):
        o = "<StatItem " + "count: " + str(self.count) + " plus: " + str(self.plus) + ">"
        return o

    def __str__(self):
        return self.__repr__()

api = Api(Config())

c = api.get_comments_from_post(1557)

def sortByCommentCount(i):
    return 0 - i.count

users = {}
for i in list(c.values()):
    if i.author in users:
        users[i.author].count += 1
    else:
        users[i.author] = StatItem(1, 0, 0, i.author)
    if i.vote_total > 0:
        users[i.author].plus += i.vote_total
    elif i.vote_total < 0:
        users[i.author].minus += math.fabs(i.vote_total)

l = list(users.values())
print(l)
l.sort(key=sortByCommentCount)
print(l)

result = ''

for i in l:
    result += '<ls user="%s" /> - комментариев: %d, плюсов: %d, минусов: %d\n'%(i.user, i.count, i.plus, i.minus)

print(result)
import time
import random
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


def rand(api, c, args):
    if len(args) > 1:
        return random.randint(int(args[0]), int(args[1]))
    elif len(args) == 1:
        return random.randint(0, int(args[0]))
    else:
        return 'Недостаточно аргументов'


def stat(api, c, args):
    comments = api.get_comments_from_post(c.post_id)

    def sortByCommentCount(i):
        return 0 - i.count

    def sortByPlus(i):
        return 0 - i.plus

    def sortByMinus(i):
        return 0 - i.minus

    users = {}
    for i in list(comments.values()):
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
    print(args)
    if len(args):
        if args[0] == 'minus':
            l.sort(key=sortByMinus)
        elif args[0] == 'plus':
            l.sort(key=sortByPlus)
        else:
            l.sort(key=sortByCommentCount)
    else:
        l.sort(key=sortByCommentCount)
    print(l)

    result = ''

    for i in l:
        result += '<a href="/profile/%s">%s</a> - комментариев: %d, плюсов: %d, минусов: %d\n' % (i.user, i.user, i.count, i.plus, i.minus)

    r = '''<span class="spoiler"><span class="spoiler-title">Статистика</span><span class="spoiler-body">
        %s
    </span></span>'''

    return r%(result)


aliases = {
    'random': rand,
    'stat': stat
}
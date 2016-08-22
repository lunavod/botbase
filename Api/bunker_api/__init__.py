import requests, re

host = 'https://bunker.lunavod.ru'


class BunkerError(Exception):
    """Класс ошибки."""
    def __init__(self, msg=None, code=0, data=None):
        self.code = int(code)
        self.message = msg if msg else code
        self.data = data
        Exception.__init__(self, self.message.encode("utf-8"))

    def __str__(self):
        return self.message

    def __unicode__(self):
        return self.message


class User(object):
    """Основной класс модуля, через него идет все взаимодействие с Бункером."""

    def __init__(self, login=None, password=None, device_uid=None):
        """Инициализация класса, логинит пользователя. Логинить обязательно, без этого почти ничего
        работать не будет.
        login - логин
        password - пароль
        device_uid - ключ для входа, его можно использовать (после установки) вместо логина и пароля.
        Устанавливается, если указать его вместе с логином и паролем. Удаляется, если указать соответствующий
        параметр при выходе."""

        if not login and not password and not device_uid:
            r = requests.post(host + '/api/version')

        else:
            data = {}

            if login and password:
                data["login"] = login
                data["password"] = password

            if device_uid:
                self.device_uid = device_uid
                data['device_uid'] = device_uid

            r = requests.post(host+'/api/login', data=data)

            if r.status_code != 200:
                raise ValueError('Вы ввели неправильный логин или пароль.')
            else:
                print(r.json())

        self.cookies = r.cookies
        self.update_security_key()


    def exit(self, delete_device_uid=False):
        """Разлогинивает. Если delete_device_uid поставить в True, сайт удалит ваш device_uid,
        в следствии чего его больше нельзя будет использовать для логина. Нужно будет задать заново."""

        data = {}

        if delete_device_uid:
            data['device_uid'] = self.device_uid

        r = requests.post(host+'/api/exit', data=data, cookies=self.cookies)
        if r.status_code != 200:
            raise BunkerError(r.json()['message'])
        else:
            print(r.json())

        self.cookes = r.cookies


    def update_security_key(self):
        """Выдирает из кода страницы security_ls_key"""

        key_sub = re.compile("LIVESTREET_SECURITY_KEY = '\w*'")
        page = requests.get(host + "/error", cookies=self.cookies).text
        key_raw = re.search(key_sub, page).group()
        self.security_key = key_raw[len("LIVESTREET_SECURITY_KEY = '"): -1]


    def add_comment(self, post_id, body, reply=0, type='blog'):
        """Добавляет комментарий. Тип - blog или talk.
        Если не указать, используется тип blog (добавление комментария к посту).
        reply - id комментария, на который нужно ответить. 0 - отправить комментарий как корневой."""

        data = {}
        data['comment_text'] = body
        data['reply'] = reply
        data['cmt_target_id'] = post_id
        data['security_ls_key'] = self.security_key

        if type not in ['blog', 'talk']:
            raise ValueError('Некорректный тип комментария.')

        r = requests.post(host + "/"+type+"/ajaxaddcomment/", data=data, cookies=self.cookies)

        if r.text == ' Hacking attemp!':
            return False

        return r.json()


    def add_post(self, blog_id, title, body, tags, draft=False, forbid_comment=False):
        """Добавляет пост. blog_id можно получить через функцию get_blog.
        draft - сохранять ли пост в черновики.
        forbid_comment - запретить ли комментировать пост."""

        data = {}
        data['topic_type'] = 'topic'
        data['blog_id'] = blog_id
        data['topic_title'] = title
        data['topic_text'] = body
        data['topic_tags'] = tags
        data['topic_forbid_comment'] = forbid_comment
        data['security_ls_key'] = self.security_key
        if draft:
            data['submit_topic_save'] = 1
        else:
            data['submit_topic_publish'] = 1
        r = requests.post(host+"/topic/add", data=data, cookies=self.cookies)
        if r.url != host+'/topic/add':
            return [True, int(r.url[r.url.rfind('/')+1:])]
        else:
            return [False, None]

    def edit_post(self, post_id, blog_id, title, body, tags, draft=False, forbid_comment=False):
        """Редактирование поста. Все то же, что и add_post, но первый параметр - id редактируемого поста."""

        data = {}
        data['topic_type'] = 'topic'
        data['blog_id'] = blog_id
        data['topic_title'] = title
        data['topic_text'] = body
        data['topic_tags'] = tags
        data['topic_forbid_comment'] = forbid_comment
        data['security_ls_key'] = self.security_key
        if draft:
            data['submit_topic_save'] = 1
        else:
            data['submit_topic_publish'] = 1
        r = requests.post(host+"/topic/edit/"+str(post_id), data=data, cookies=self.cookies)
        if r.url != host+'/topic/edit/'+str(post_id):
            return [True, int(r.url[r.url.rfind('/')+1:])]
        else:
            return [False, None]


    def get_post(self, post_id, comments=None):
        """Получение поста по id.
        comments может быть id или full. При id пост возвращается вместе с id комментов из него,
        при full - с самими комментами."""

        data = {}

        if comments not in [None, 'full', 'id']:
            raise ValueError()

        if comments:
            data['comments']=comments

        r = requests.get(host+"/api/posts/"+str(post_id), params=data, cookies=self.cookies)

        if 'error' in r.json().keys():
            raise BunkerError(r.json()['error'])

        return r.json()


    def get_comment(self, comment_id):
        """Получение одного коммента по id."""

        data = {}

        data['id'] = comment_id

        r = requests.get(host + "/api/comments/stream", params=data, cookies=self.cookies)

        if 'error' not in r.json().keys():
            return r.json()
        else:
            raise BunkerError(r.json()['error'])


    def get_blog(self, blog):
        """Получение блога по url или id.
        Если аргумент - число, или строка, состоящая из цифр, функция определяет, что это id.
        Если нет - как url.
        url - название блога в url (а не полный url). Т.е. для http://bunker.lunavod.ru/blog/flud/
        url будет flud."""

        data ={}

        if str(blog).isdigit():
            data['id'] = blog
        else:
            data['url'] = blog
        print(data)
        r = requests.get(host + "/api/blog", params=data, cookies=self.cookies)

        if 'error' not in r.json().keys():
            return r.json()
        else:
            raise BunkerError(r.json()['error'])

    def get_stream(self, page=1, comments='full'):
        """Получение прямого эфира. page - страница. На каждой странице 20 комментов.
        Возвращает словарь с id комментов."""
        data = {}
        data['comments'] = comments
        data['page'] = page

        r = requests.get(host + '/api/comments/stream', params=data, cookies=self.cookies)
        return r.json()
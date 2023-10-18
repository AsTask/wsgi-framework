from framework.http.request import env, url, method, cookie, Path
from framework.http.response import set_cookie, delete_cookie, url_for, url_file, set_header, has_header, delete_header


def index():
    set_header('test', 'header')
    set_header('delete', 'test')
    print(has_header('delete'))
    delete_header('delete')
    print(has_header('delete'))
    return env('SERVER_PROTOCOL')


def redirect():
    # set_header('location', url_file('test.css'))
    # return b'', 307
    return b'', 307, [('location', url_file('test.css'))]


def extension(path: Path):
    set_cookie('cookie', 'test')
    delete_cookie('cookie')
    print('cookie:', cookie('cookie'))
    print('query:', url.get('query'))
    return f"extension: {path['ext']}"


class Page:
    def __call__(self, path: Path):
        print(url_file('test.css'))
        print(url_for('page', year='2023', month='10', day='17', slug='slug?query=value'))
        return f"{self.__class__.__name__}: {path}"


class Error:
    def __call__(self, *args, **kwargs):
        return f"{self.__class__.__name__}: call"

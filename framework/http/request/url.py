from ...alias import WSGIEnvironment

__env: WSGIEnvironment
__dict: dict[str, str]


def scheme() -> str:
    return __env["wsgi.url_scheme"]


def host() -> str:
    return __env["HTTP_HOST"]


def path() -> str:
    return __env["PATH_INFO"]


def query() -> str:
    return __env["QUERY_STRING"]


def request() -> str:
    return __env["REQUEST_URI"]


def get(name: str):
    return __dict.get(name)

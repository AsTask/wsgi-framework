from ...alias import WSGIEnvironment

__env: WSGIEnvironment
__dict: dict[str, str]


def env(name: str):
    return __env.get(name)


def method() -> str:
    return __env['REQUEST_METHOD']


def user_address() -> str:
    return __env['REMOTE_ADDR']


def user_agent() -> str:
    return __env['HTTP_USER_AGENT']


def cookie(name: str):
    return __dict.get(name)


class Path:
    __slots__ = ('__token',)

    __token: dict[str, int | float | str]

    def __init__(self, tokens: dict[str, int | float | str]):
        self.__token = tokens

    def __getitem__(self, key: str):
        return self.__token[key]

    def __repr__(self):
        return self.__token.__repr__()

    def has(self, name: str):
        return name in self.__token.keys()

    def get(self, name: str) -> int | float | str | None:
        return self.__token.get(name)

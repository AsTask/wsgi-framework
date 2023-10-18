import re
import sys
from typing import Any, Iterable

from . import request, response, Map
from .request import url, Path
from .response import cookies
from ..alias import StartResponse, WSGIEnvironment


def configure(url_map: Map, static_url: str, media_type: str, encoding: str):
    for slot, obj in ((a, getattr(url_map, a)) for a in url_map.__slots__):
        if 'link' == slot:
            for attr, value in ((slot, obj), ('static_url', static_url)):
                setattr(response, f"__{attr}", value)

        else:
            setattr(Routing, f"_Routing__{slot}", obj)

    for attr, value in (('media_type', media_type), ('encoding', encoding)):
        setattr(MimeTypes, f"_MimeTypes__{attr}", value)


class Generic:
    __slots__ = ('body', 'code', 'headers', 'media_type', 'encoding')

    body: bytes
    code: int
    headers: list[tuple[str, str]]
    media_type: str
    encoding: str

    def __init__(self, environ: WSGIEnvironment):
        for module in (request, url):
            setattr(module, '__env', environ)

        for module in (request, url, response, cookies):
            setattr(module, '__dict', dict())

        if 'HTTP_COOKIE' in environ:
            cookie = getattr(request, '__dict')

            for k in environ['HTTP_COOKIE'].split('; '):
                key, value = k.split('=')

                cookie[key] = value

        if query_string := environ['QUERY_STRING']:
            query = getattr(url, '__dict')

            for k in query_string.split("&"):
                key, value = (q := k.split('=', 1))[0], q[1] if 1 < len(q) else ''

                query[key] = value

        self.code = 200


class MimeTypes(Generic):
    __slots__ = ('__media_type', '__encoding')

    __media_type: str
    __encoding: str

    def unpack(
            self,
            body: Any,
            code: int = None,
            headers: list[tuple[str, str]] = None,
            media_type: str = None,
            encoding: str = None,
    ):
        self.encoding = self.__encoding if encoding is None else encoding

        if isinstance(body, bytes):
            self.body = body

        elif isinstance(body, str):
            self.body = body.encode(self.encoding)

        else:
            self.body = b''

        if code is not None:
            self.code = code

        self.headers = list(getattr(response, '__dict').items())

        if headers is not None:
            self.headers.extend(headers)

        for cookie in getattr(cookies, '__dict').values():
            self.headers.append(('set-cookie', cookie))

        self.media_type = self.__media_type if media_type is None else media_type


class Routing(MimeTypes):
    __slots__ = ('__pattern', '__endpoint')

    __pattern: dict[str, tuple[str, tuple[tuple[int, str], ...]]]
    __endpoint: dict[str, tuple[str | None, str, str, tuple[Any, ...]]]

    def __init__(self, environ: WSGIEnvironment):
        super().__init__(environ)

        link, kwargs = self.parse(environ['PATH_INFO'])

        if link is None:
            unpack = b'Not Found', 404

        else:
            method, module, name, args = self.__endpoint[link]

            __import__(module)
            call = getattr(sys.modules[module], name)

            if method is not None:
                call = getattr(call(), method)

            unpack = call(*args, **kwargs)

        if isinstance(unpack, tuple):
            self.unpack(*unpack)

        else:
            self.unpack(unpack)

    def parse(self, path_info: str):
        link, kwargs = None, dict()

        for pattern, items in self.__pattern.items():
            if values := re.findall(pattern, path_info):
                (link, types), values = items, v if isinstance((v := values[0]), tuple) else (v,)

                if 0 < values.__len__() == types.__len__():
                    tokens, i = dict(), 0

                    for flag, key in types:
                        match flag:
                            case 0:
                                tokens[key] = values[i]

                            case 1:
                                tokens[key] = int(values[i])

                            case 2:
                                tokens[key] = float(values[i])

                        i += 1

                    kwargs['path'] = Path(tokens)

                break

        return link, kwargs

    def __call__(self, start_response: StartResponse) -> Iterable[bytes]:
        size = len(self.body)

        if self.media_type.startswith('text'):
            if size:
                self.media_type = f"{self.media_type}{';'} charset={self.encoding}"

        self.headers.extend([('content-length', str(size)), ('content-type', self.media_type)])

        start_response((codes := {
            200: '200 OK',
            307: '307 Temporary Redirect',
            308: '308 Permanent Redirect',
            404: '404 Not Found',
            520: '520 Unknown Error',
        })[self.code if self.code in codes.keys() else 520], self.headers)

        yield self.body

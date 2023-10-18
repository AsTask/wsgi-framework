import re

from .cookies import set_cookie, delete_cookie

__link: dict[str, tuple[tuple[str, str, tuple[str, ...]], ...]]
__static_url: str
__dict: dict[str, str]


def _url(link: tuple[tuple[str, str, tuple[str, ...]], ...], kwargs: dict[str, int | float | str]):
    for pattern, path, keys in link:
        if (i := kwargs.__len__()) == keys.__len__():
            if 0 < i:
                for key in keys:
                    try:
                        path, query = path.replace(f"<{key}>", kwargs[key]), ''

                        if 1 < len(s := path.split('?', 1)):
                            path, query = s[0], f"?{s[1]}"

                        if hasattr(r := re.match(pattern, path), 'string'):
                            return f"{r.string}{query}"

                    except KeyError:
                        pass

            else:
                return path


def url_for(name: str, **kwargs):
    if link := __link.get(name):
        return _url(link, kwargs)


def url_file(path: str):
    return f"{__static_url}{path}"


def set_header(name: str, value: str):
    __dict[name.lower()] = value


def has_header(name: str):
    return name.lower() in __dict.keys()


def delete_header(name: str):
    if (name := name.lower()) in __dict.keys():
        del __dict[name]

import re
from typing import Any, Callable


class Rule:
    __slots__ = ('path', 'link', 'tokens')

    def __init__(self, path: str, link: str, tokens: dict[str, str | tuple[int, str]] = None):
        for attr, value in (
                ('path', path),
                ('link', link),
                ('tokens', dict() if tokens is None else tokens),
        ):
            setattr(self, attr, value)


class Endpoint:
    __slots__ = ('link', 'method', 'module', 'name', 'args')

    def __init__(self, link: str, endpoint: Callable | tuple[Callable] | tuple[Callable, str], *args):
        if isinstance(endpoint, tuple):
            obj, method = endpoint[0], '__call__' if 1 == len(endpoint) else endpoint[1]

        else:
            obj, method = endpoint, '__call__' if isinstance(endpoint, type) else None

        for attr, value in (
                ('link', link),
                ('method', method),
                ('module', obj.__module__),
                ('name', obj.__name__),
                ('args', args),
        ):
            setattr(self, attr, value)


class Map:
    __slots__ = ('link', 'pattern', 'endpoint')

    def __init__(self, rules: tuple[Rule | Endpoint, ...]):
        def generator():
            return (getattr(line, a) for a in line.__slots__)

        for attr in ('link', 'pattern', 'endpoint'):
            setattr(self, attr, dict())

        for line in rules:
            match line.__class__.__name__:
                case 'Rule':
                    self.rule(*generator())

                case 'Endpoint':
                    self.linking(*generator())

    def rule(self, path: str, link: str, path_tokens: dict[str, str]):
        def msg(message: str, *args):
            return f"in url Map > in Rule > {message}" % args

        assert isinstance(path, str), \
            'in url Map > in Rule > the path must be a string type'

        assert path, \
            'in url Map > in Rule > path must not be an empty string'

        assert path.startswith('/'), msg(
            "path must start slash: '%s'", path
        )

        raw_path, pattern, keys, types = path, f"^{path}$", tuple(), tuple()

        for key in re.findall(r'<([A-Za-z0-9:_,)(]+)>', path):
            if 1 < len(s := str(key).split(':', 1)):
                (raw_flag, key), replace = s, key

                if 'int' == raw_flag:
                    flag, value = 1, r'\d+'

                elif r := re.findall(r'^int\(([0-9,]+)\)$', raw_flag):
                    flag, value, raw_flag = 1, r'\d{%s}' % r[0], 'int'

                else:
                    flag, value = 2, r'\d+\.\d+'

                assert raw_flag in ('int', 'float'), msg(
                    "path token has an invalid flag: '%s'", replace
                )

                path = path.replace(f"<{replace}>", f"<{key}>")
                pattern = pattern.replace(f"<{replace}>", f"({value})")

            else:
                flag, value = 0, path_tokens.pop(key, None)

                if value is None:
                    value = r'[A-Za-z0-9_-]+'

                if isinstance(value, tuple):
                    flag, value = value

                assert flag in (0, 1, 2), msg(
                    "the added token has an invalid type flag: (%s, '%s')", flag, value
                )

                pattern = pattern.replace(f"<{key}>", f"({value})")

            keys = (*keys, key)
            types = (*types, (flag, key))

        assert {} == path_tokens, msg(
            'tokens added to rules have unused values: %s', path_tokens
        )

        assert pattern not in self.pattern.keys(), msg(
            "path already exists in pattern list: '%s'", raw_path
        )

        if link in self.link.keys():
            self.link[link] = (*self.link[link], (pattern, path, keys))

        else:
            self.link[link] = ((pattern, path, keys),)

        self.pattern[pattern] = link, types

    def linking(self, link: str, method: str | None, module: str, name: str, args: tuple[Any, ...]):
        assert link not in self.endpoint.keys(), \
            "in url Map > in Endpoint > link already exists in endpoint list: '%s'" % link

        self.endpoint[link] = method, module, name, args

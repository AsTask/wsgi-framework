from datetime import datetime, timedelta
from time import gmtime, time
from typing import Any, Literal

__dict: dict[str, str]


def set_cookie(
        key: str,
        value: str,
        expires: datetime | int | str = None,
        max_age: timedelta | int = None,
        domain: str = None,
        path: str = '/',
        secure: bool = False,
        httponly: bool = False,
        samesite: Literal['lax', 'strict', 'none'] = None,
):
    cookie = Cookie(key, value)

    if expires is not None:
        cookie['Expires'] = expires

    if max_age is not None:
        if isinstance(max_age, timedelta):
            max_age = max_age.seconds

        if expires is None:
            cookie['Expires'] = max_age

        cookie['Max-Age'] = max_age

    if domain is not None:
        cookie['Domain'] = domain

    for k, v in (('Path', path), ('HttpOnly', httponly), ('Secure', secure)):
        cookie[k] = v

    if samesite is not None:
        assert samesite in ('lax', 'none', 'strict'), \
            f"in func set_cookie samesite='{samesite}' must be 'lax', 'none', or 'strict'"

        cookie['SameSite'] = samesite

    __dict[key] = cookie.as_string()


def delete_cookie(key: str, path: str = "/", domain: str = None):
    set_cookie(key, '', 'Thu, 01 Jan 1970 00:00:00 GMT', 0, domain, path)


def format_datetime(timestamp: float):
    weekdayname = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    monthname = [None, 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    year, month, day, hh, mm, ss, wd, yd, z = gmtime(timestamp)

    return '%s, %02d %3s %4d %02d:%02d:%02d GMT' % (weekdayname[wd], day, monthname[month], year, hh, mm, ss)


class Cookie:
    __slots__ = ('__cookie',)

    def __init__(self, key: str, value: str):
        self.__cookie = f"{key}={value}"

    def __setitem__(self, key: str, value: Any):
        if value is True:
            self.flag(key)

        elif key in ('Domain', 'Path'):
            self.add(key, value)
        else:
            match key:
                case 'Expires':
                    self.expires(key, value)

                case 'Max-Age':
                    self.add(key, str(value))

                case 'SameSite':
                    self.add(key, value.capitalize())

    def flag(self, key: str):
        self.__cookie = f"{self.__cookie}; {key}"

    def add(self, key: str, value: str):
        self.__cookie = f"{self.__cookie}; {key}={value}"

    def expires(self, key: str, value: datetime | int | str):
        if isinstance(value, datetime):
            self.add(key, format_datetime(datetime.timestamp(value)))

        elif isinstance(value, int):
            self.add(key, format_datetime(time() + value))

        else:
            self.add(key, value)

    def as_string(self):
        return self.__cookie

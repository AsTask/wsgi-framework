from framework import Framework
from framework.http import Rule, Endpoint, Map

from src.model import index, redirect, extension, Page, Error

url_map = Map((
    Rule('/', 'main'),
    Endpoint('main', index),

    Rule('/redirect', 'redirect'),
    Endpoint('redirect', redirect),

    Rule('/extension.<float:ext>', 'extension'),
    Endpoint('extension', extension),

    Rule('/page/<int(4):year>/', 'page'),
    Rule('/page/<int(4):year>/<int(2):month>/', 'page'),
    Rule('/page/<int(4):year>/<int(2):month>/<int(2):day>/', 'page'),
    Rule('/page/<int(4):year>/<int(2):month>/<int(2):day>/<slug>', 'page'),
    Endpoint('page', Page),

    # Rule(1, 'error'),
    # Rule('', 'error'),
    # Rule('path', 'error'),
    # Rule('/error/<error:token>/', 'error'),
    # Rule('/error/<token>/', 'error', {'token': (9, r'\w+')}),
    # Rule('/error/<int:year>', 'error', {'year': r'\d{4}'}),
    # Rule('/error', 'error'),
    # Rule('/error', 'error'),
    # Endpoint('error', Error),
    # Endpoint('error', Error),
))

app = Framework(__name__, url_map)

# app = Framework(__name__, static_url='url/')
# app = Framework(__name__, static_url='/url')
# app = Framework(__name__, static_url=1)

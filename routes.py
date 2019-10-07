import pathlib

from views import index


def setup_routes(app):
    app.router.add_get('/', index, name='index')
    app.router.add_static('/static', f'{pathlib.Path(__file__).parent}/static')

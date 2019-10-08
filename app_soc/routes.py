import pathlib

from app_soc.views import index, registration


def setup_routes(app):
    app.router.add_get('/', index, name='index')
    app.router.add_get('/registration', registration, name='registration')
    app.router.add_static('/static', f'{pathlib.Path(__file__).parent}/static')

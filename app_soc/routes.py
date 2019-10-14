import pathlib

from aiohttp import web

from app_soc.views import index, SignIn, Login


def setup_routes(app: web.Application):
    app.router.add_static('/static', f'{pathlib.Path(__file__).parent.parent}/static', name='static')

    app.router.add_get('/', index, name='main')
    app.router.add_view('/login', Login, name='login')
    app.router.add_view('/registration', SignIn, name='registration')


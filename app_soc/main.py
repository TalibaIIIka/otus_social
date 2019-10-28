#!/usr/bin/env python3
import base64
import logging
import os
import sys

import aiohttp_jinja2
import aiohttp_session
import jinja2
import uvloop
from aiohttp import web
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from cryptography import fernet

from app_soc.db import init_mysql, close_mysql
from app_soc.routes import setup_routes
from app_soc.settings import get_config, BASE_DIR


def init_app(argv=None):
    app = web.Application()

    app['static_root_url'] = '/static'
    app['config'] = get_config(argv)

    app.on_startup.append(init_mysql)
    app.on_cleanup.append(close_mysql)

    setup_routes(app)

    aiohttp_jinja2.setup(
        app,
        loader=jinja2.PackageLoader('app_soc', 'templates')
    )

    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    aiohttp_session.setup(app, EncryptedCookieStorage(secret_key))
    return app


def main(argv):
    logging.basicConfig(
        filename=BASE_DIR/'log'/'social_demo.log',
        level=logging.DEBUG
    )
    app = init_app(argv)

    config = get_config(argv)
    uvloop.install()
    web.run_app(
        app,
        host=config['host'],
        port=os.environ.get('PORT') or config['port']
    )


if __name__ == '__main__':
    main(sys.argv[1:])

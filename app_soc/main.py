#!/usr/bin/env python3
import logging
import sys

import aiohttp_jinja2
import jinja2
from aiohttp import web

from app_soc.db import init_mysql, close_mysql
from app_soc.routes import setup_routes
from app_soc.settings import get_config


def init_app(argv=None):
    app = web.Application()

    app['config'] = get_config(argv)

    app.on_startup.append(init_mysql)
    app.on_cleanup.append(close_mysql)

    setup_routes(app)

    aiohttp_jinja2.setup(
        app,
        loader=jinja2.PackageLoader('app_soc', 'templates')
    )

    return app


def main(argv):
    logging.basicConfig(level=logging.DEBUG)
    app = init_app(argv)

    config = get_config(argv)
    web.run_app(
        app,
        host=config['host'],
        port=config['port']
    )


if __name__ == '__main__':
    main(sys.argv[1:])

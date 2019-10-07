#!/usr/bin/env python3
import aiohttp_jinja2
import jinja2
from aiohttp import web

from routes import setup_routes


def init_app():
    app = web.Application()

    aiohttp_jinja2.setup(
        app,
        loader=jinja2.FileSystemLoader('templates'),
    )

    return app


def main():
    app = init_app()
    setup_routes(app)
    web.run_app(app, port=8080)


if __name__ == '__main__':
    main()

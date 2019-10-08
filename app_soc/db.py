import os

import aiomysql


async def init_mysql(app):
    config = app['config']
    dsn = os.environ.get('DATABASE_URL', config['mysql'])
    app['db_pool'] = await aiomysql.create_pool(**dsn)


async def close_mysql(app):
    app['db_pool'].close()
    await app['db_pool'].wait_closed()

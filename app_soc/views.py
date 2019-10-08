import aiohttp_jinja2


@aiohttp_jinja2.template('index.html')
async def index(request):
    # username = await authorized_userid(request)
    # if not username:
    #     raise redirect(request.app.router, 'login')

    # async with request.app['db_pool'].acquire() as conn:
    #     current_user = await db.get_user_by_name(conn, username)
    #     posts = await db.get_posts_with_joined_users(conn)

    return {}


@aiohttp_jinja2.template('registration.html')
async def registration(request):
    return {}

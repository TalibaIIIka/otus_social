import asyncio
import logging
from collections import defaultdict
from random import choice

import aiohttp_jinja2
from aiohttp import web

import aiohttp_session

from app_soc.db import User, ErrorUserAlreadyExist


@aiohttp_jinja2.template('index.html')
async def index(request: web.Request):
    session = await aiohttp_session.get_session(request)
    user_id = session.get('user_id')
    if not user_id:
        location = request.app.router['login'].url_for()
        raise web.HTTPFound(location=location)

    person_data = defaultdict(str)
    person_data.update({'id_account': user_id})
    user = User(choice(request.app['db_pool_slave']), person_data)
    return await user.get_info()


@aiohttp_jinja2.template('registration.html')
async def registration(request: web.Request):
    return {}


class SignIn(web.View):
    @aiohttp_jinja2.template('registration.html')
    async def get(self):
        return {}

    @aiohttp_jinja2.template('registration.html')
    async def post(self):
        person_form_data = await self.request.post()
        person_data = defaultdict(str)
        person_data.update(person_form_data)

        try:
            user = User(self.request.app['db_pool'], person_data)
            user_id = await user.create_user()
            logging.info('Create user. USER_ID: %s', user_id)
            session = await aiohttp_session.get_session(self.request)
            session['user_id'] = user_id
            url = self.request.app.router['main'].url_for()
            return web.HTTPFound(location=url)
        except ErrorUserAlreadyExist:
            person_data.update({'user_valid': 'is-invalid'})
            return person_data
        except Exception:
            logging.exception('Create user')


class Login(web.View):

    @aiohttp_jinja2.template('login.html')
    async def get(self):
        session = await aiohttp_session.get_session(self.request)
        user_id = session.get('user_id')
        if user_id:
            url = self.request.app.router['main'].url_for()
            raise web.HTTPFound(location=url)
        return {}

    @aiohttp_jinja2.template('login.html')
    async def post(self):
        person_form_data = await self.request.post()
        person_data = defaultdict(str)
        person_data.update(person_form_data)

        try:
            user = User(choice(self.request.app['db_pool_slave']), person_data)
            if not await user.check_user():
                person_data.update({'user_valid': 'is-invalid'})
                return person_data

            user_id = await user.check_auth()
            if not user_id:
                person_data.update({'password_valid': 'is-invalid'})
                return person_data

            session = await aiohttp_session.get_session(self.request)
            session['user_id'] = user_id
            url = self.request.app.router['main'].url_for()
            return web.HTTPFound(location=url)
        except Exception:
            logging.exception('Cannot login')


class SearchEngine(web.View):
    @aiohttp_jinja2.template('find_user.html')
    async def get(self):
        return {}

    @aiohttp_jinja2.template('find_user.html')
    async def post(self):
        person_form_data = await self.request.post()
        person_data = defaultdict(str)
        person_data.update(person_form_data)
        try:
            user = User(choice(self.request.app['db_pool_slave']), person_data)
            find_users = await user.find_user_by_name_surname(prefix=person_data['prefix_name'])
            return {
                'users': find_users,
                'name': person_data['prefix_name'],
            }
        except asyncio.CancelledError:
            logging.warning('web-handlers was cancelled on client disconnection')
        except Exception:
            logging.exception('Cannot find')

import asyncio
import os
from string import Template
from urllib.parse import urlparse

import aiomysql
import scrypt
from Crypto.Random import get_random_bytes


async def init_mysql(app):
    config = app['config']
    dsn = os.environ.get('DATABASE_URL', '')
    dsn_dict = None
    if dsn:
        dsn_parse = urlparse(dsn)
        dsn_dict = {
            'host': dsn_parse.hostname,
            'port': 3306,
            'user': dsn_parse.username,
            'password': dsn_parse.password,
            'db': dsn_parse.path.strip('/')
        }
    dsn = dsn_dict or config['mysql']

    pool: aiomysql.Pool
    pool = await aiomysql.create_pool(**dsn)
    app['db_pool'] = pool

    async with pool.acquire() as conn:
        await init_db(conn)


async def close_mysql(app):
    app['db_pool'].close()
    await app['db_pool'].wait_closed()


async def init_db(conn: aiomysql.Connection) -> None:
    from app_soc.settings import BASE_DIR
    with open(BASE_DIR/'app_soc'/'sql'/'create_tables.sql') as sql_file:
        sql_create_db = sql_file.read()

    cur: aiomysql.Cursor
    async with conn.cursor() as cur:
        await cur.execute(sql_create_db)


class ErrorUserAlreadyExist(Exception):
    pass


class User:
    def __init__(self, pool: aiomysql.Pool, person):
        self.db_pool = pool
        self.id_account = person.get('id_account')
        self.username = person.get('username')
        self.password = person.get('password')
        self.name = person.get('name')
        self.surname = person.get('surname')
        self.sex = person.get('sex')
        self.birthday = person.get('birthday')
        self.city = person.get('city')
        self.interests = person.get('interests')

    async def is_user_exist(self):
        select_username = f"""
            SELECT count(*) FROM accounts 
                WHERE username='{self.username}'
        """
        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(select_username)
                (count,) = await cur.fetchone()
                return count != 0

    async def create_user(self):
        if await self.is_user_exist():
            raise ErrorUserAlreadyExist
        salt = get_random_bytes(16)
        password_hash = scrypt.hash(self.password, salt)
        sql_create_account = f"""
            INSERT INTO accounts (username, salt, password_hash) 
                VALUES ('{self.username}', '{salt.hex()}', '{password_hash.hex()}');
        """
        conn: aiomysql.Connection
        cur: aiomysql.Cursor
        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql_create_account)
                account_id = cur.lastrowid
                sql_create_user = f"""
                    INSERT INTO users (id_account, name, surname, birthday, 
                                           sex, interests, city)
                        VALUES ('{account_id}', '{self.name}', '{self.surname}', '{self.birthday}', 
                        '{self.sex}', '{self.interests}', '{self.city}');
                """
                await cur.execute(sql_create_user)
                await conn.commit()
                return account_id

    async def check_user(self):
        select_user = f"""
            SELECT count(*) FROM accounts
              WHERE username='{self.username}' 
        """
        conn: aiomysql.Connection
        cur: aiomysql.Cursor
        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(select_user)
                (count, ) = await cur.fetchone()
                return count

    async def check_auth(self):
        select_salt_hash = f"""
            SELECT salt, password_hash, id_account FROM accounts
              WHERE username='{self.username}'
        """

        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(select_salt_hash)
                (salt, password_hash, id_account) = await cur.fetchone()
        if scrypt.hash(self.password, bytes.fromhex(salt)).hex() == password_hash:
            return id_account
        return None

    async def get_info(self):
        select_info = f"""
            SELECT * FROM users
              WHERE id_account={self.id_account}
        """
        async with self.db_pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(select_info)

                return await cur.fetchone()

    async def find_user_by_name_surname(self, prefix=None):
        if not prefix:
            return []

        t = Template("""
            SELECT id_account as id, name, surname, birthday, sex, interests, city
                FROM users
                WHERE name like '$prefix%' OR surname like '$prefix%' ORDER BY id;
        """)
        sql_find = t.substitute(prefix=prefix)
        async with self.db_pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(sql_find)
                return await cur.fetchall()

    async def create_user_alter(self, account_id, conn):
        salt = 'c7569ba8f3b6adcfa9fc52eb8f285157'
        password_hash = '1c742a8f6824fbb145405e322f3183cb17f15ee59be00c2fa72a14b5369dffde9415a83b849af6370e7a7c5ab2f21a84e53ebfc66daae76ff24ff6782b4dadba'
        sql_create_account = f"""
            INSERT INTO accounts (id_account, username, salt, password_hash) 
                VALUES ('{account_id}', '{self.username}', '{salt}', '{password_hash}');
        """
        sql_create_user = f"""
                        INSERT INTO users (id_account, name, surname, birthday, 
                                               sex, interests, city)
                            VALUES ('{account_id}', '{self.name}', '{self.surname}', '{self.birthday}', 
                            '{self.sex}', '{self.interests}', '{self.city}');
                    """
        conn: aiomysql.Connection
        cur: aiomysql.Cursor

        async with conn.cursor() as cur:
            await cur.execute(sql_create_account)

            await cur.execute(sql_create_user)

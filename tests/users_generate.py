import asyncio
import concurrent.futures
from random import random
from collections import defaultdict

import aiomysql
from faker import Faker

from app_soc.db import User


DSN = {
    'host': 'us-cdbr-iron-east-05.cleardb.net',
    'port': 3306,
    'user': 'b079c24dda06b6',
    'password': '30817953412ce1c',
    'db': 'heroku_fd253ea686e5ee8'
}

DSN_HYPER = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'user',
    'password': 'social',
    'db': 'social',
    'minsize': 1,
    'maxsize': 5,
    'connect_timeout': 3,
    'no_delay': False,
    'autocommit': False
}

DSN_AWS = {
    'host': 'ec2-18-222-39-34.us-east-2.compute.amazonaws.com',
    'port': 3306,
    'user': 'user',
    'password': 'social',
    'db': 'social',
    'minsize': 1,
    'maxsize': 10,
    'connect_timeout': 5,
    'no_delay': False,
    'autocommit': False
}

fake = Faker('ru_RU')


def user_generate_fake():
    person = defaultdict(str)

    if random() > 0.5:
        sex = 'M'
    else:
        sex = 'F'
    if sex == 'M':
        person['name'] = fake.first_name_male()
    else:
        person['name'] = fake.first_name_female()
    if sex == 'M':
        person['surname'] = fake.last_name_male()
    else:
        person['surname'] = fake.last_name_female()
    person['sex'] = sex
    person['username'] = fake.user_name()
    person['password'] = '1111'

    person['birthday'] = fake.date()

    person['city'] = fake.city()

    person['interests'] = fake.text(max_nb_chars=66)

    # salt = get_random_bytes(16)
    # password_hash = scrypt.hash('1111', salt)

    person['salt'] = 'c7569ba8f3b6adcfa9fc52eb8f285157'
    person['password_hash'] = '1c742a8f6824fbb145405e322f3183cb17f15ee59be00c2fa72a14b5369dffde9415a83b849af6370e7a7c5ab2f21a84e53ebfc66daae76ff24ff6782b4dadba'

    return person


COUNTER = 1


async def generate_fake_accounts(pool: aiomysql.pool):
    global COUNTER
    try:
        loop = asyncio.get_event_loop()
        async with pool.acquire() as conn:
            for i in range(100_000):
                person = user_generate_fake()     #await loop.run_in_executor(None, user_generate_fake)
                fake_user = User(conn, person)
                account_id = COUNTER
                COUNTER += 1

                await fake_user.create_user_alter(account_id, conn)
                if i % 501 == 0:
                    await conn.commit()
            await conn.commit()
    except Exception as exc:
        print(exc)
    finally:
        pool.close()
        await pool.wait_closed()


async def main():
    pool = await aiomysql.create_pool(**DSN_AWS)
    tasks = []
    for _ in range(10):
        tasks.append(generate_fake_accounts(pool))
    await asyncio.gather(*tasks)


def generate_csv():
    with open('/opt/social/generate_acc.csv', 'w') as f_acc, open('/opt/social/generate_user.csv', 'w') as f_user:
        for i in range(1_000_000):
            user = user_generate_fake()
            str_acc = f"{i},{user['salt']},{user['password_hash']},{user['username']}\n"
            str_user = f"{i},{user['name']},{user['surname']},{user['birthday']},{user['sex']},{user['interests']},{user['city']}\n"
            f_acc.write(str_acc)
            f_user.write(str_user)


if __name__ == '__main__':
    # loop = asyncio.get_event_loop()
    # executor = concurrent.futures.ProcessPoolExecutor(
    #     max_workers=4,
    # )
    # loop.set_default_executor(executor)
    asyncio.run(main())
    # generate_csv()

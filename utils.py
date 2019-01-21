from time import time

from aiopg import create_pool
from aioredis import create_redis
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, User

from settings import TTL, R_HOST, R_PORT, DB_PARAMS
from tasks import send_last_update


def get_cancel_button() -> InlineKeyboardMarkup:
    """
    Return inline keyboard with 'Stop tracking' button
    :return:
    """
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('Stop updating', callback_data='::'))
    return keyboard


async def init_redis_track(user_id: int, message_id: int, station_id: int,
                           loop) -> None:
    """
    Coro. This function inits update process by putting to redis dict with
    data that needs to update
    :param user_id:
    :param message_id:
    :param station_id:
    :param loop:
    :return:
    """
    data = {
        'id': user_id,
        'station': station_id,
        'updated': int(time()),
        'message_id': message_id,
        'expire': int(time()) + int(TTL)
    }

    r = await create_redis(f'redis://{R_HOST}:{R_PORT}', loop=loop,
                           encoding='utf-8')

    # if user already in redis, we need to finish his old message updating
    # process end init new one
    user_in_redis = await r.exists(user_id)
    if user_in_redis:
        old_data = await r.hgetall(user_id)  # get data about old message
        # run celery task that will finish old update process
        # run synchronously, because we need to wait until the task will work
        # out before initialise the new process
        send_last_update(old_data)

    await r.hmset_dict(user_id, data)
    r.close()
    await r.wait_closed()


async def stop_redis_track(user_id: int, loop) -> None:
    """
    Coro. This function inits last-time-updating of user message by reducing
    'expire' value
    :param user_id:
    :param loop:
    :return:
    """
    r = await create_redis(f'redis://{R_HOST}:{R_PORT}', loop=loop)
    await r.hset(key=user_id, field='expire', value=int(time()))
    r.close()
    await r.wait_closed()


async def check_user(user: User):
    async with create_pool(DB_PARAMS) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                query = f'INSERT INTO users \
                          VALUES \
                          ( \
                            {user.id}, {user.first_name}, \
                            {user.last_name}, {user.username} \
                          ) \
                          ON CONFLICT DO NOTHING'
                await cur.execute(query)


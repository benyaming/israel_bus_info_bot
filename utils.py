from aiopg import create_pool
from aiopg.pool import Pool
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, User


from settings import DB_PARAMS


def get_cancel_button() -> InlineKeyboardMarkup:
    """
    Return inline keyboard with 'Stop tracking' button
    :return:
    """
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('Stop updating', callback_data='::'))
    return keyboard


async def check_user(user: User, pool: Pool = None):
    async with create_pool(DB_PARAMS) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                query = f'INSERT INTO users \
                          VALUES \
                          ( \
                            {user.id}, \'{user.first_name}\', \
                            \'{user.last_name}\', \'{user.username}\' \
                          ) \
                          ON CONFLICT DO NOTHING'
                await cur.execute(query)



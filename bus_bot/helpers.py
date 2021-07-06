from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, User
from aiogram import Dispatcher


class CallbackPrefix:
    stop_updates = 'stop_updates:'
    get_stop = 'stop:'


def get_cancel_button(station: int) -> InlineKeyboardMarkup:
    """
    Return inline keyboard with 'Stop tracking' button
    :return:
    """
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('Stop updating', callback_data=f'{CallbackPrefix.stop_updates}{station}'))
    return keyboard


async def check_user():
    user = User.get_current()
    pool = Dispatcher.get_current()['db_pool']

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            query = f'''INSERT INTO users 
                        VALUES 
                        (%s, %s, %s, %s) 
                        ON CONFLICT DO NOTHING'''
            await cur.execute(query, (user.id, user.first_name, user.last_name, user.username))



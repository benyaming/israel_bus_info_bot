from dataclasses import dataclass
from typing import Optional

from aiopg import create_pool
from aiopg.pool import Pool
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, User
from aiogram import Dispatcher


@dataclass
class UserData:
    user_id: int
    station_id: int
    message_id: int
    next_station_id: Optional[int] = False
    next_message_id: Optional[int] = False
    stop_updating: bool = False


def get_cancel_button(station: str) -> InlineKeyboardMarkup:
    """
    Return inline keyboard with 'Stop tracking' button
    :return:
    """
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('Stop updating', callback_data=f'{station}'))
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



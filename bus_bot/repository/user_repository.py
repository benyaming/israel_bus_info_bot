from datetime import datetime as dt
from typing import Optional

import aiogram_metrics
from aiogram.types import User as TelegramUser

from bus_bot.misc import db_engine
from .models import User, PersonalDetails, SavedStop


__all__ = ['check_user']

from ..exceptions import StopAlreadySaved


async def check_user(user_id: int, first_name: str, last_name: Optional[str], username: str, locale: str):
    user = await db_engine.find(User, User.id == user_id)
    if user:
        user = user[0]
        user.last_seen = dt.now()
    else:
        pd = PersonalDetails(first_name=first_name, last_name=last_name, username=username, locale=locale)
        user = User(id=user_id, personal_details=pd)
        aiogram_metrics.manual_track('New user Joined')

    await db_engine.save(user)


async def get_user(user_id: int) -> User:
    user = await db_engine.find(User, User.id == user_id)
    if not user:
        tg_user = TelegramUser.get_current()
        await check_user(tg_user.id, tg_user.first_name, tg_user.last_name, tg_user.username, tg_user.language_code)
        return await get_user(user_id)
    return user[0]


# Saved stops management
async def get_user_saved_stops(user_id: int) -> list[SavedStop]:
    user = await get_user(user_id)
    return user.saved_stops


async def save_stop(user_id: int, stop_code: int, stop_name: str) -> list[SavedStop]:
    user = await get_user(user_id)
    stop = SavedStop(name=stop_name, code=stop_code)
    if user.is_stop_already_saved(stop_code):
        raise StopAlreadySaved()

    user.saved_stops.append(stop)

    await db_engine.save(user)
    return user.saved_stops


async def rename_stop(user_id: int, stop_code: int, new_name: str) -> list[SavedStop]:
    user = await get_user(user_id)
    stop = list(filter(lambda s: s.code == stop_code, user.saved_stops))
    if not stop:
        raise ValueError('Trying to update non-existing saved stop!')

    stop = stop[0]
    stop_index = user.saved_stops.index(stop)
    user.saved_stops[stop_index].name = new_name
    await db_engine.save(user)
    return user.saved_stops


async def remove_stop(user_id: int, stop_code: int) -> list[SavedStop]:
    user = await get_user(user_id)
    stop = list(filter(lambda s: s.code == stop_code, user.saved_stops))
    if not stop:
        raise ValueError('Trying to delete non-existing saved stop!')

    stop = stop[0]
    user.saved_stops.remove(stop)
    await db_engine.save(user)
    return user.saved_stops

from datetime import datetime as dt
from typing import Optional

import aiogram_metrics
from bus_bot.misc import db_engine

from .models import User, PersonalDetails


__all__ = ['check_user']


async def check_user(user_id: int, first_name: str, last_name: Optional[str], username: str, locale: str):
    user = await db_engine.find(User, User.id == user_id)
    now = dt.now()
    if user:
        user = user[0]
        user.last_seen = now
    else:
        pd = PersonalDetails(first_name=first_name, last_name=last_name, username=username, locale=locale)
        user = User(id=user_id, last_seen=now, personal_details=pd)
        aiogram_metrics.manual_track('New user Joined')

    await db_engine.save(user)





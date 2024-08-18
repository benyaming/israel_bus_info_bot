from typing import Callable, Any, Awaitable

from aiogram.types import Update

from bus_bot.repository.user_repository import DbRepo


async def check_user_middleware(handler: Callable[[Update, Any], Awaitable], event: Update, data: Any):
    if event.message:
        user = event.message.from_user
    elif event.callback_query:
        user = event.callback_query.from_user
    else:
        return await handler(event, data)

    db_repo: DbRepo = data['db_repo']
    await db_repo.check_user(user)

    return await handler(event, data)

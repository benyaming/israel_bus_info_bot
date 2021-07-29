from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Update

from bus_bot.repository.user_repository import check_user


class CheckUserMiddleware(BaseMiddleware):

    @staticmethod
    async def on_pre_process_update(update: Update, _):
        if update.message:
            user = update.message.from_user
        elif update.callback_query:
            user = update.callback_query.from_user
        else:
            return

        await check_user(
            user_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            locale=user.language_code
        )

from aiogram import Dispatcher

from .check_user_middleware import check_user_middleware
from .sentry_middleware import sentry_context_middleware


__all__ = ['register_middlewares']


def register_middlewares(dp: Dispatcher):
    dp.update.outer_middleware.register(sentry_context_middleware)
    dp.update.outer_middleware.register(check_user_middleware)

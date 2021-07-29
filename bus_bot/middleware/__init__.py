from bus_bot.misc import dp

from .check_user_middleware import CheckUserMiddleware
from .sentry_middleware import SentryContextMiddleware


__all__ = ['register_middlewares']


def register_middlewares():
    dp.middleware.setup(SentryContextMiddleware())
    dp.middleware.setup(CheckUserMiddleware())

from typing import Callable, Any, Awaitable

import sentry_sdk
from aiogram.types import Update


async def sentry_context_middleware(handler: Callable[[Update, Any], Awaitable], event: Update, data: Any):
    if event.message or event.callback_query:
        sentry_sdk.set_user({
            'id': (event.message or event.callback_query).from_user.id,
            'update': event.model_dump()
        })

    return await handler(event, data)

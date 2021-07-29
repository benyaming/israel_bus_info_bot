from aiogram.types import ContentTypes, ContentType
from aiogram.utils.exceptions import MessageNotModified

from bus_bot.clients.bus_api.exceptions import StationNonExistsException, ApiNotRespondingException, NoStopsException
from bus_bot.helpers import CallbackPrefix
from bus_bot.misc import dp

from . import errors
from . import helpers
from . import commands
from . import bus_handlers


__all__ = ['register_handlers']


def register_handlers():
    # errors
    dp.register_errors_handler(errors.on_err_not_modified, exception=MessageNotModified)
    dp.register_errors_handler(errors.on_err_station_not_exists, exception=StationNonExistsException)
    dp.register_errors_handler(errors.on_err_api_not_responding, exception=ApiNotRespondingException)
    dp.register_errors_handler(errors.on_err_not_stations_found, exception=NoStopsException)
    dp.register_errors_handler(errors.on_err_unknown_exception, exception=Exception)  # Should be last in this list!

    # commands
    dp.register_message_handler(commands.on_start_command, commands=['start'])
    dp.register_message_handler(commands.on_help_command, commands=['help'])

    # messages
    dp.register_message_handler(
        bus_handlers.on_stop_code,
        lambda msg: msg.text.isdigit(),
        content_types=ContentTypes.TEXT
    )
    dp.register_callback_query_handler(
        bus_handlers.on_terminate_call,
        text_startswith=CallbackPrefix.stop_updates
    )
    dp.register_message_handler(bus_handlers.on_location, content_types=[ContentType.LOCATION, ContentType.VENUE])
    dp.register_callback_query_handler(bus_handlers.on_stop_call, text_startswith=CallbackPrefix.get_stop)

    # THIS ONE SHOULD BE LAST
    dp.register_message_handler(helpers.incorrect_message_handler)

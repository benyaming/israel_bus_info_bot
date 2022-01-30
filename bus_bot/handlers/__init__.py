from aiogram.dispatcher.filters import Filter, Text
from aiogram.types import ContentTypes, ContentType
from aiogram.utils.exceptions import MessageNotModified

from bus_bot.clients.bus_api.exceptions import StationNonExistsError, ApiNotRespondingError, NoStopsError
from bus_bot.helpers import CallbackPrefix
from bus_bot.misc import dp

from . import forms
from . import errors
from . import helpers
from . import commands
from . import bus_handlers


__all__ = ['register_handlers']

from .. import texts
from ..exceptions import StopAlreadySaved

from ..states import RenameStopState


def register_handlers():
    # errors
    dp.register_errors_handler(errors.on_err_not_modified, exception=MessageNotModified)
    dp.register_errors_handler(errors.on_err_station_not_exists, exception=StationNonExistsError)
    dp.register_errors_handler(errors.on_err_api_not_responding, exception=ApiNotRespondingError)
    dp.register_errors_handler(errors.on_err_api_timeout, exception=ApiNotRespondingError)
    dp.register_errors_handler(errors.on_err_not_stations_found, exception=NoStopsError)
    dp.register_errors_handler(errors.on_err_stop_already_saved, exception=StopAlreadySaved)
    dp.register_errors_handler(errors.on_err_unknown_exception, exception=Exception)  # Should be last in this list!

    dp.register_message_handler(helpers.on_cancel, text_startswith=texts.cancel_button, state='*')  # Should be first after error handlers!

    # commands
    dp.register_message_handler(commands.on_start_command, commands=['start'], state='*')
    dp.register_message_handler(commands.on_help_command, commands=['help'])
    dp.register_message_handler(commands.on_saved_stops_command, commands=['my_stops'])

    # messages
    dp.register_message_handler(
        bus_handlers.on_stop_code,
        lambda msg: msg.text.isdigit(),
        content_types=ContentTypes.TEXT
    )
    dp.register_message_handler(bus_handlers.on_location, content_types=[ContentType.LOCATION, ContentType.VENUE])

    # callbacks
    dp.register_callback_query_handler(bus_handlers.on_terminate_call, text_startswith=CallbackPrefix.terminate_stop_updating)
    dp.register_callback_query_handler(bus_handlers.on_stop_call,text_startswith=[CallbackPrefix.get_stop, CallbackPrefix.get_saved_stop])
    dp.register_callback_query_handler(bus_handlers.on_save_stop, text_startswith=CallbackPrefix.save_stop)
    dp.register_callback_query_handler(bus_handlers.on_remove_stop, text_startswith=CallbackPrefix.remove_stop)
    dp.register_callback_query_handler(bus_handlers.on_track_call, text_startswith=CallbackPrefix.track_route)

    # forms
    dp.register_message_handler(forms.on_stop_rename, state=RenameStopState.waiting_for_stop_name)

    # THIS ONE SHOULD BE LAST
    dp.register_message_handler(helpers.incorrect_message_handler)

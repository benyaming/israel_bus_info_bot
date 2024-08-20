from aiogram import F, Dispatcher
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.exception import ExceptionTypeFilter


from bus_bot.clients.bus_api.exceptions import StationNonExistsError, ApiNotRespondingError, NoStopsError
from bus_bot.exceptions import StopAlreadySaved
from bus_bot.handlers import errors
from bus_bot.handlers.forms import router as forms_router
from bus_bot.handlers.helpers import incorrect_message_router, cancel_router
from bus_bot.handlers.commands import router as commands_router
from bus_bot.handlers.bus_handlers import router as bus_handlers_router


__all__ = ['register_handlers']


def register_handlers(dp: Dispatcher):
    # errors
    dp.error.register(errors.on_err_not_modified, ExceptionTypeFilter(TelegramBadRequest))
    dp.error.register(errors.on_err_station_not_exists, ExceptionTypeFilter(StationNonExistsError))
    dp.error.register(errors.on_err_api_not_responding, ExceptionTypeFilter(ApiNotRespondingError))
    dp.error.register(errors.on_err_api_timeout, ExceptionTypeFilter(ApiNotRespondingError))
    dp.error.register(errors.on_err_not_stations_found, ExceptionTypeFilter(NoStopsError))
    dp.error.register(errors.on_err_stop_already_saved, ExceptionTypeFilter(StopAlreadySaved))
    dp.error.register(errors.on_err_unknown_exception, ExceptionTypeFilter(Exception))  # Should be last in this list!

    dp.include_router(cancel_router)  # Should be first after error handlers!
    dp.include_router(commands_router)
    dp.include_router(bus_handlers_router)
    dp.include_router(forms_router)
    dp.include_router(incorrect_message_router)

from bus_bot.exceptions import BotError


class StationNonExistsError(BotError):
    ...


class ApiNotRespondingError(BotError):
    ...


class NoStopsError(BotError):
    ...


exception_by_codes = {
    1: StationNonExistsError,
    3: ApiNotRespondingError
}

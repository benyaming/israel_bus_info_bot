class BotException(Exception):
    ...


class StationNonExistsException(BotException):
    ...


class ApiNotRespondingException(BotException):
    ...


class NoStopsException(BotException):
    ...


exception_by_codes = {
    1: StationNonExistsException,
    3: ApiNotRespondingException
}

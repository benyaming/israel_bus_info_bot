from typing import Union

from bus_bot.bus_api import get_lines


async def handle_text(text: Union[str, int]) -> dict:
    """
    Coro. Entrypoint for all text messages. Filters incorrect text
    :param text: text from message
    :return: text response: {'ok': True|False, 'data': bus_data|error mess}
    """
    response = {'ok': True}
    # check if text correct
    if text.isdigit():
        bus_data = await get_lines(int(text))
        if bus_data:
            # append bus data to response dict
            response['data'] = bus_data
            response['station_id'] = text
        else:
            # if text is correct, but station number is invalid
            response['ok'] = False
            response['data'] = _get_error_message('invalid_station')
    else:
        # if text is incorrect
        response['ok'] = False
        response['data'] = _get_error_message('incorrect_text')
    return response


def _get_error_message(error_type: str) -> str:
    """
    Not coro. Use this func for get different error messages
    :param error_type: 'incorrect_text' or 'invalid_station'
    :return: error message for user
    """
    error_message = {
        'incorrect_text': 'Text is incorrect, send station number!',
        'invalid_station': 'Invalid station number!'
    }
    return error_message.get(error_type)

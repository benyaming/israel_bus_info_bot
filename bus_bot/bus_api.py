from typing import Union

from aiohttp import request
from aiogram import Bot


URL = 'http://mabat.mot.gov.il/AdalyaService.svc/StationLinesByIdGet'


async def get_lines(station_id: int, last: bool = False) -> Union[str, bool]:
    """
    Coro. This coro func makes request to mabat bus api, and forms shiny
    message with lines that arrives soon.
    :param station_id:
    :param last: if true, add `Message not updating!` title after message
    :return: string message if success, with markdown for telegram
    """
    # data for request to api
    json_data = {
        "stationId": station_id,
        "isSIRI": True,
        "lang": "1037"
    }

    # making request
    async with request('POST', URL, json=json_data) as r:
        res = await r.json()

    try:
        # if station id valid
        lines = res['Payload']['Lines']
        station_name = res['Payload']['StationInfo']['StationName']
    except TypeError:
        # if station id invalid
        return False

    buses = []  # list that collects all lines

    # extract useful data from response and accumulating in lines list
    for line in lines:
        bus = dict()
        bus['bus_number'] = line['LineSign']
        bus['minutes'] = line['EstimationTime']
        bus['target_city'] = line['TargetCityName']
        buses.append(bus)

    bus_list = [f'<b>{station_name}</b>\n']  # list with formatted lines

    # formatting each line in lines list and collect them to formatted list
    for i in buses:
        bus_number = i["bus_number"]
        target = i['target_city']
        time = f'{i["minutes"]} min' if i['minutes'] != 0 else 'now'
        if 'א' in i['bus_number']:
            bus_str = f'\u200E🚌 <code>{bus_number:<5}</code>\u200E 🕓 <code>{time:<7}</code> ' \
                f'🏙️ \u200E{target}\u200E'
            bus_list.append(bus_str)
        else:
            bus_list.append(f'🚌 <code>{bus_number:<5}</code> 🕓 <code>{time:<7}</code> '
                            f'🏙️ \u200E{target}\u200E')

    # making string from formatted list
    status = '<i>Information is updating...</i>' if not last else '<b>Message not updating!</b>'
    response = '\n'.join(bus_list)
    response = f'{response}\n\n{status}'

    return response


async def is_station_valid(station: str) -> bool:
    session = Bot.get_current().session

    json = {
        "stationId": station,
        "isSIRI": True,
        "lang": "1037"
    }
    async with session.post(URL, json=json) as resp:
        resp = await resp.json()
        try:
            station_info = resp['Payload']['StationInfo']
        except (TypeError, KeyError):
            return False
        if not station_info:
            return False

        return True

from typing import List

from bus_bot.bus_api_v2.exceptions import ApiNotRespondingException, StationNonExistsException
from bus_bot.misc import session
from bus_bot.bus_api_v2.models import LineInfo
from bus_bot.config import STOP_INFO_URL, ARRIVING_LINES_URL


async def get_station_name(station_id: int) -> str:
    async with session.get(STOP_INFO_URL.format(station_id)) as resp:
        if resp.status > 400:
            raise ApiNotRespondingException()

        data: dict = await resp.json()
        name = data.get('Name')
        if not name:
            raise StationNonExistsException()

        return name


async def get_lines_for_station(station_id: int) -> List[LineInfo]:
    async with session.get(ARRIVING_LINES_URL.format(station_id)) as resp:
        if resp.status > 400:
            raise ApiNotRespondingException()

        data = await resp.json()
        arriving_lines = [LineInfo(**line_data) for line_data in data]
        return arriving_lines


async def prepare_station_schedule(station_id: int, is_last_update: bool = False) -> str:
    station_name = await get_station_name(station_id)
    arriving_lines = await get_lines_for_station(station_id)

    response_lines = [f'<b>{station_name}</b>\n']

    for line in arriving_lines:
        eta = f'{line.minutes_to_arrival} min' if line.minutes_to_arrival != 0 else 'now'

        # some black RTL/LTR magic
        if 'א' in line.bus_number:
            bus_str = f'\u200E🚌 <code>{line.bus_number:<5}</code>\u200E 🕓 <code>{eta:<7}</code> ' \
                      f'🏙️ \u200E{line.destination}\u200E'
            response_lines.append(bus_str)
        else:
            response_lines.append(f'🚌 <code>{line.bus_number:<5}</code> 🕓 <code>{eta:<7}</code> '
                                  f'🏙️ \u200E{line.destination}\u200E')

    status = '<i>\n\nInformation is updating...</i>' if not is_last_update else '<b>\n\nMessage not updating!</b>'
    response_lines.append(status)

    response = '\n'.join(response_lines)
    return response

import logging
from typing import List

from bus_bot.bus_api_v3.exceptions import ApiNotRespondingException, StationNonExistsException
from bus_bot.bus_api_v3.models import IncomingRoutesResponse
from bus_bot.misc import session
from bus_bot.config import API_URL


logger = logging.getLogger('bus_api')


async def get_lines_for_station(station_id: int) -> IncomingRoutesResponse:
    url = f'{API_URL}/siri/get_routes_for_stop/{station_id}'
    async with session.get(url) as resp:
        if resp.status > 400:
            logger.exception((await resp.read()).decode('utf-8'))
            raise ApiNotRespondingException()

        data = await resp.json()
        arriving_lines = IncomingRoutesResponse(**data)
        return arriving_lines


async def prepare_station_schedule(station_id: int, is_last_update: bool = False) -> str:
    arriving_lines = await get_lines_for_station(station_id)

    response_lines = [f'<b>{arriving_lines.stop_info.name}</b>\n']

    for route in arriving_lines.incoming_routes:
        eta = f'{route.eta} min' if route.eta != 0 else 'now'

        # some black RTL/LTR magic
        if 'א' in route.route.short_name:
            bus_str = f'\u200E🚌 <code>{route.route.short_name:<5}</code>\u200E 🕓 <code>{eta:<7}</code> ' \
                      f'🏙️ \u200E{route.route.to_city}\u200E'
            response_lines.append(bus_str)
        else:
            response_lines.append(f'🚌 <code>{route.route.short_name:<5}</code> 🕓 <code>{eta:<7}</code> '
                                  f'🏙️ \u200E{route.route.to_city}\u200E')

    status = '<i>\n\nInformation is updating...</i>' if not is_last_update else '<b>\n\nMessage not updating!</b>'
    response_lines.append(status)

    response = '\n'.join(response_lines)
    return response

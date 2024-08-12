import logging
from typing import List

from pydantic import parse_obj_as

from bus_bot.clients.bus_api.exceptions import exception_by_codes, ApiNotRespondingError, ApiTimeoutError
from bus_bot.clients.bus_api.models import IncomingRoutesResponse, Stop, IncomingRoute
from bus_bot.misc import session
from bus_bot.config import env


__all__ = ['find_near_stops', 'prepare_station_schedule', 'get_stop_info']

logger = logging.getLogger('bus_api_client')

TRANSPORT_ICONS = {
    '2': '🚄',
    '3': '🚌'
}


def _format_lines(routes: list[IncomingRoute]) -> list[str]:
    lines = []

    for route in routes:
        eta = f'{route.eta} min' if route.eta != 0 else 'now'

        # some black RTL/LTR magic
        transport_icon = TRANSPORT_ICONS.get(route.route.type, '❔')
        time_icon = '🔥' if route.eta == 0 else '🕓'

        if 'א' in route.route.short_name:
            bus_str = f'\u200E{transport_icon} <code>{route.route.short_name:<5}</code>\u200E {time_icon} ' \
                      f'<code>{eta:<7}</code> 🏙️ \u200E{route.route.to_city}\u200E'
            lines.append(bus_str)
        else:
            lines.append(f'{transport_icon} <code>{route.route.short_name:<5}</code> {time_icon} <code>{eta:<7}</code> '
                         f'🏙️ \u200E{route.route.to_city}\u200E')
    return lines


async def _get_lines_for_station(station_id: int) -> IncomingRoutesResponse:
    url = f'{env.API_URL}/siri/get_routes_for_stop/{station_id}'

    try:
        resp = await session.get(url)
    except Exception as e:
        logger.error(f'{e}: failed to open api url [{url}]!')
        raise ApiNotRespondingError()

    if resp.status_code > 400:
        logging.error((resp.read()).decode('utf-8'))
        try:
            body = resp.json()
        except Exception as e:
            raise ApiTimeoutError
        resp.raise_for_status()

        code = body.get('detail', {}).get('code', 3)
        exc = exception_by_codes.get(code, ApiNotRespondingError)

        logger.error(body)
        raise exc()

    data = resp.json()
    arriving_lines = IncomingRoutesResponse(**data)
    return arriving_lines


async def find_near_stops(lat: float, lng: float) -> List[Stop]:
    url = f'{env.API_URL}/stop/near'
    params = {'lat': lat, 'lng': lng, 'radius': 200}

    try:
        resp = await session.get(url, params=params)
    except Exception as e:
        logger.error(f'{e}: failed to open api url [{url}]!')
        raise ApiNotRespondingError()

    if resp.status_code > 400:
        body = resp.json()
        code = body.get('detail', {}).get('code', 3)
        exc = exception_by_codes.get(code, 3)

        logger.error(body)
        raise exc
    resp.raise_for_status()

    data = resp.json()
    stops = parse_obj_as(List[Stop], data)

    # temporary solution to delete stops with same id (such as central stations platforms)
    unique_stops = {stop.code: stop for stop in stops}
    return list(unique_stops.values())


async def prepare_station_schedule(station_id: int, is_last_update: bool = False) -> str:
    arriving_lines = await _get_lines_for_station(station_id)
    response_lines = [f'<b>{arriving_lines.stop_info.name} ({arriving_lines.stop_info.code})</b>\n']

    if arriving_lines.incoming_routes:
        formatted_lines = _format_lines(arriving_lines.incoming_routes)
    else:
        formatted_lines = ['<code>No incoming routes found for the next 30 minutes...</code>']

    response_lines.extend(formatted_lines)
    status = '<i>\n\nInformation is updating...</i>' if not is_last_update else '<b>\n\nMessage is not updating!</b>'
    response_lines.append(status)

    response = '\n'.join(response_lines)
    return response


async def get_stop_info(stop_code: int) -> Stop:
    url = f'{env.API_URL}/stop/by_code/{stop_code}'

    try:
        resp = await session.get(url)
    except Exception as e:
        logger.error(f'{e}: failed to open api url [{url}]!')
        raise ApiNotRespondingError()

    if resp.status_code > 400:
        body = resp.json()
        code = body.get('detail', {}).get('code', 3)
        exc = exception_by_codes.get(code, 3)

        logger.error(body)
        raise exc
    resp.raise_for_status()

    data = resp.json()
    stop = Stop(**data)
    return stop

import logging

from pydantic import TypeAdapter
from httpx import AsyncClient

from bus_bot.clients.bus_api.exceptions import exception_by_codes, ApiNotRespondingError, ApiTimeoutError
from bus_bot.clients.bus_api.models import IncomingRoutesResponse, Stop, IncomingRoute, StopType
from bus_bot.config import env


__all__ = ['find_near_stops', 'prepare_stop_schedule', 'get_stop_by_code', 'get_stop_by_id']

logger = logging.getLogger('bus_api_client')

TRANSPORT_ICONS = {
    2: '🚄',
    3: '🚌'
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


def filter_out_unsupported_stop_types(stops: list[Stop]) -> list[Stop]:
    """
    Filters out stops that are not supported by the bot.
    Supported stop types are bus stops, bus central stations, and railway stations.
    """
    unsupported_types = {
        StopType.bus_central_station_platform,
        StopType.gush_dan_light_rail_platform
    }
    return [stop for stop in stops if stop.stop_type not in unsupported_types]


async def _get_lines_for_stop(stop_id: int, session: AsyncClient) -> IncomingRoutesResponse:
    url = f'{env.API_URL}/siri/get_routes_for_stop_by_id/{stop_id}'

    try:
        resp = await session.get(url)
    except Exception as e:
        logger.error(f'{e}: failed to open api url [{url}]!')
        raise ApiNotRespondingError()

    if resp.status_code > 400:
        logging.error((resp.read()).decode('utf-8'))
        try:
            body = resp.json()
        except Exception as _:
            raise ApiTimeoutError

        code = body.get('detail', {}).get('code', 3)
        exc = exception_by_codes.get(code, ApiNotRespondingError)

        logger.error(body)
        raise exc()

    data = resp.json()
    arriving_lines = IncomingRoutesResponse(**data)
    return arriving_lines


async def prepare_stop_schedule(station_id: int, session: AsyncClient, is_last_update: bool = False) -> str:
    arriving_lines = await _get_lines_for_stop(station_id, session)
    
    if arriving_lines.stop_info.platform is None:
        response_lines = [f'<b>{arriving_lines.stop_info.name} ({arriving_lines.stop_info.code})</b>\n']
    else:
        response_lines = [
            f'<b>{arriving_lines.stop_info.name} ({arriving_lines.stop_info.code})</b> '
            f'(platform {arriving_lines.stop_info.platform})\n'
        ]

    if arriving_lines.incoming_routes:
        formatted_lines = _format_lines(arriving_lines.incoming_routes)
    else:
        formatted_lines = ['<code>No incoming routes found for the next 30 minutes...</code>']

    response_lines.extend(formatted_lines)
    status = '<i>\n\nInformation is updating...</i>' if not is_last_update else '<b>\n\nMessage is not updating!</b>'
    response_lines.append(status)

    response = '\n'.join(response_lines)
    return response


async def find_near_stops(lat: float, lng: float, session: AsyncClient) -> list[Stop]:
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
    stops = TypeAdapter(list[Stop]).validate_python(data)
    stops = filter_out_unsupported_stop_types(stops)
    stops.sort(key=lambda stop: (-stop.location.coordinates[0], stop.location.coordinates[1]))
    return stops


async def get_stop_by_code(stop_code: int, session: AsyncClient) -> Stop:
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


async def get_stop_by_id(stop_id: int, session: AsyncClient) -> Stop:
    url = f'{env.API_URL}/stop/by_id/{stop_id}'

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


async def get_stop_by_parent_id(parent_stop_id: int, session: AsyncClient) -> list[Stop]:
    url = f'{env.API_URL}/stop/by_parent_id/{parent_stop_id}'

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
    stops = TypeAdapter(list[Stop]).validate_python(data)
    return stops

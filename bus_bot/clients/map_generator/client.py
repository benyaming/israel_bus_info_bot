import json
import logging
from io import BytesIO
from typing import List, Tuple
from urllib.parse import quote

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bus_bot.config import env
from bus_bot.clients.bus_api.client import find_near_stops
from bus_bot.clients.bus_api.exceptions import NoStopsError
from bus_bot.clients.bus_api.models import Stop
from bus_bot.misc import session
from bus_bot.helpers import CallbackPrefix


__all__ = ['get_map_with_points']

logger = logging.getLogger('map_generator_client')

MAP_ZOOM = 15.5
STILE_ID = 'mapbox/streets-v11'
IMG_SIZE = '500x500'


def _get_marker_color(stop: Stop) -> str:
    if stop.floor == 'תחנת רכבת' or stop.city is None:
        color = '#066ed6'
    else:
        color = 'd60606'
    return color


def _get_encoded_geojson_from_stops(stops: List[Stop]) -> str:
    features = []
    for i, stop in enumerate(stops, 1):
        features.append(
            {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [stop.location.coordinates[1], stop.location.coordinates[0]]
                },
                'properties': {
                    'marker-color': _get_marker_color(stop),
                    'marker-symbol': str(i)
                }
            }
        )
    geojson = {'type': 'FeatureCollection', 'features': features}
    return quote(json.dumps(geojson))


def _get_kb_for_stops(stops: List[Stop]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    for i, stop in enumerate(stops, 1):
        kb.row(InlineKeyboardButton(
            text=f'{i} — {stop.name} ({stop.code})',
            callback_data=f'{CallbackPrefix.get_stop}{stop.code}'
        ))
    return kb


async def get_map_with_points(lat: float, lng: float) -> Tuple[BytesIO, InlineKeyboardMarkup]:
    stops = await find_near_stops(lat, lng)
    if len(stops) == 0:
        raise NoStopsError

    params = {
        'access_token': env.MAPBOX_TOKEN
    }

    geojson_query = _get_encoded_geojson_from_stops(stops)
    map_query = f'auto'
    # map_query = f'{lng},{lat},{MAP_ZOOM},0,0'
    url = f'https://api.mapbox.com/styles/v1/{STILE_ID}/static/geojson({geojson_query})/{map_query}/{IMG_SIZE}'

    try:
        resp = await session.get(url, params=params)
    except Exception as e:
        logger.error(f'{e}: failed to open api url!')
        raise ValueError('Failed to generate map!')

    if resp.headers.get('Content-Type') != 'image/png':
        logger.exception(resp.read())
        raise ValueError('Failed to generate map!')

    io = BytesIO()
    io.write(resp.read())
    io.seek(0)

    kb = _get_kb_for_stops(stops)
    return io, kb

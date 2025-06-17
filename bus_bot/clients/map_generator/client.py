import json
import logging
from io import BytesIO
from urllib.parse import quote

from aiogram.types import InlineKeyboardMarkup
from httpx import AsyncClient

from bus_bot.config import env
from bus_bot.clients.bus_api.models import Stop, StopType


__all__ = ['get_map_with_points']

logger = logging.getLogger('map_generator_client')

MAP_ZOOM = 15.5
STILE_ID = 'mapbox/streets-v11'
IMG_SIZE = '500x500'
IMG_SIZE_LARGE = '850x850'


MARKER_COLORS = {
    StopType.gush_dan_light_rail_station: '#a611a1',
    StopType.jerusalem_light_rail_stop: '#FF7C2C',
    StopType.railway_station: '#066ed6',
    StopType.bus_stop: '#d60606',
    StopType.bus_central_station: '#078f04'
}


def _get_encoded_geojson_from_stops(stops: list[Stop]) -> str:
    features = []
    
    unique_stops = {stop.code: stop for stop in stops}
    
    for i, stop in enumerate(unique_stops.values(), 1):
        features.append(
            {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [stop.location.coordinates[1], stop.location.coordinates[0]]
                },
                'properties': {
                    'marker-color': MARKER_COLORS.get(stop.stop_type, '#d60606'),
                    'marker-symbol': str(i)
                }
            }
        )
    geojson = {'type': 'FeatureCollection', 'features': features}
    return quote(json.dumps(geojson))


async def get_map_with_points(stops: list[Stop], session: AsyncClient) -> tuple[BytesIO, InlineKeyboardMarkup]:
    params = {
        'access_token': env.MAPBOX_TOKEN
    }

    geojson_query = _get_encoded_geojson_from_stops(stops)
    map_query = f'auto'
    # map_query = f'{lng},{lat},{MAP_ZOOM},0,0'
    img_size = IMG_SIZE_LARGE if len(stops) > 10 else IMG_SIZE
    
    url = f'https://api.mapbox.com/styles/v1/{STILE_ID}/static/geojson({geojson_query})/{map_query}/{img_size}'

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

    return io


'''
# todo
platform kb
marker colors
'''

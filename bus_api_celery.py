from typing import Union

from requests import post


URL = 'http://mabat.mot.gov.il/AdalyaService.svc/StationLinesByIdGet'


def get_lines(station_id: int) -> Union[str, bool]:
    """
    This function is sync version of bus_api.get_lines. It needs because
    celery cant working with python's asyncio. Except request to api,
    function's body is absolutely same as async version
    :param station_id:
    :return:
    """
    json_data = {
        "stationId": station_id,
        "isSIRI": True,
        "lang": "1037"
    }

    with post(URL, json=json_data) as r:
        res = r.json()
        try:
            lines = res['Payload']['Lines']
            station_name = res['Payload']['StationInfo']['StationName']
        except TypeError:
            return False

        buses = []
        for line in lines:
            bus = dict()
            bus['bus_number'] = line['LineSign']
            bus['minutes'] = line['EstimationTime']
            bus['target_city'] = line['TargetCityName']
            buses.append(bus)

        bus_list = [f'*{station_name}*\n']
        for i in buses:
            bus_number = i["bus_number"]
            target = i['target_city']
            time = f'{i["minutes"]} min' if i['minutes'] != 0 else 'now'
            if 'א' in i['bus_number']:
                bus_str = f'\u200E🚌 `{bus_number:<5}`\u200E 🕓 `{time:<7}` ' \
                    f'🏙️ \u200E{target}\u200E'
                bus_list.append(bus_str)
            else:
                bus_list.append(f'🚌 `{bus_number:<5}` 🕓 `{time:<7}` '
                                f'🏙️ \u200E{target}\u200E')
        result = '\n'.join(bus_list)

        return result

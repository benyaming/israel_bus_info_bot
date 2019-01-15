import aiohttp


URL = 'http://mabat.mot.gov.il/AdalyaService.svc/StationLinesByIdGet'


async def get_lines(station_id: int) -> dict:
    json_data = {
        "stationId": station_id,
        "isSIRI": True,
        "lang": "1037"
    }

    async with aiohttp.request('POST', URL, json=json_data) as r:
        res = await r.json()
        try:
            lines = res['Payload']['Lines']
            station_name = res['Payload']['StationInfo']['StationName']
        except TypeError:
            return {'ok': False}

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
        response = '\n'.join(bus_list)

        result = {'ok': True, 'data': response}
        return result


import requests


URL = 'http://mabat.mot.gov.il/AdalyaService.svc/StationLinesByIdGet'


def get_bus_info(stop_id: int) -> str:
    json_data = {
        "stationId": stop_id,
        "isSIRI": True,
        "lang": "1037"
    }

    r = requests.post(
        URL,
        json=json_data
    )

    res = r.json()

    lines = res['Payload']['Lines']
    station_name = res['Payload']['StationInfo']['StationAddress']

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
            bus_str = f'\u200E🚌 `{bus_number:<5}`\u200E 🕓 {time:<7} ' \
                      f'🏙️ \u200E{target}\u200E'
            bus_list.append(bus_str)
        else:
            bus_list.append(f'🚌 `{bus_number:<5}` 🕓 `{time:<7}` '
                            f'🏙️ \u200E{target}\u200E')
    response = '\n'.join(bus_list)

    # print(response)
    return response

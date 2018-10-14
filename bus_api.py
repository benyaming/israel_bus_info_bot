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
        buses.append(bus)

    bus_list = [f'*{station_name}*\n']
    for i in buses:
        bus_list.append(f'🚌 `{i["bus_number"]:<5}` 🕓 {i["minutes"]} min')
    response = '\n'.join(bus_list)
    return response

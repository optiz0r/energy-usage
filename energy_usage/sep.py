""" SEP protocol parser
"""
import datetime
import json


def parse_sep(topic, payload_str):
    """
    
    Credit to https://gist.github.com/ndfred/b373eeafc4f5b0870c1b8857041289a9

    :param topic: str Topic SEP payload was received from
    :param payload_str: str SEP payload message as a string
    :return: 
    """
    payload = json.loads(payload_str)
    timestamp = datetime.datetime.fromtimestamp(payload["gmtime"], tz=datetime.timezone.utc)
    electricity_consumption = int(payload["elecMtr"]["0702"]["04"]["00"], 16)
    electricity_daily_consumption = int(payload["elecMtr"]["0702"]["04"]["01"], 16)
    electricity_weekly_consumption = int(payload["elecMtr"]["0702"]["04"]["30"], 16)
    electricity_monthly_consumption = int(payload["elecMtr"]["0702"]["04"]["40"], 16)
    electricity_multiplier = int(payload["elecMtr"]["0702"]["03"]["01"], 16)
    electricity_divisor = int(payload["elecMtr"]["0702"]["03"]["02"], 16)
    electricity_meter = int(payload["elecMtr"]["0702"]["00"]["00"], 16)
    electricity_mpan = payload["elecMtr"]["0702"]["03"]["07"]
    gas_daily_consumption = int(payload["gasMtr"]["0702"]["0C"]["01"], 16)
    gas_weekly_consumption = int(payload["gasMtr"]["0702"]["0C"]["30"], 16)
    gas_monthly_consumption = int(payload["gasMtr"]["0702"]["0C"]["40"], 16)
    gas_multiplier = int(payload["gasMtr"]["0702"]["03"]["01"], 16)
    gas_divisor = int(payload["gasMtr"]["0702"]["03"]["02"], 16)
    gas_meter = int(payload["gasMtr"]["0702"]["00"]["00"], 16)
    gas_mpan = payload["gasMtr"]["0702"]["03"]["07"]
    device_gid = payload["gid"]

    assert(int(payload["elecMtr"]["0702"]["03"]["00"], 16) == 0) # kWh
    assert(int(payload["gasMtr"]["0702"]["03"]["01"], 16) == 1) # m3
    assert(int(payload["gasMtr"]["0702"]["03"]["12"], 16) == 0) # kWh

    data = {
        'timestamp': timestamp,
        'tags': {
            'topic': topic,
            'gid': device_gid,
        },
        'electricity': {
            'tags': {
                'mpan': electricity_mpan,
            },
            'metrics': {
                'draw': electricity_consumption * electricity_multiplier / electricity_divisor,
                'consumption_daily': electricity_daily_consumption * electricity_multiplier / electricity_divisor,
                'consumption_weekly': electricity_weekly_consumption * electricity_multiplier / electricity_divisor,
                'consumption_monthly': electricity_monthly_consumption * electricity_multiplier / electricity_divisor,
                'meter_reading': electricity_meter * electricity_multiplier / electricity_divisor,
            },
        },
        'gas': {
            'tags': {
                'mpan': gas_mpan,
            },
            'metrics': {
                'consumption_daily': gas_daily_consumption * gas_multiplier / gas_divisor,
                'consumption_weekly': gas_weekly_consumption * gas_multiplier / gas_divisor,
                'consumption_monthly': gas_monthly_consumption * gas_multiplier / gas_divisor,
                'meter_reading': gas_meter * gas_multiplier / gas_divisor,
            },
        },
    }

    return data


def usage_to_datapoints(usage):
    datapoints = []

    for utility in ['electricity', 'gas']:
        datapoints.append({
            "measurement": utility,
            "tags": {**usage['tags'], **usage[utility]['tags']},
            "time": usage['timestamp'].isoformat(),
            "fields": usage[utility]['metrics'],
        })

    return datapoints

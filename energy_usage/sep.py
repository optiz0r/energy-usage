""" SEP protocol parser
"""
import datetime
import json
import logging


def parse_sep(topic, payload_str):
    """
    
    Credit to https://gist.github.com/ndfred/b373eeafc4f5b0870c1b8857041289a9

    :param topic: str Topic SEP payload was received from
    :param payload_str: str SEP payload message as a string
    :return:
    """
    logger = logging.getLogger(__name__)

    def _get_metric(path, type=int):
        value = payload
        try:
            for hop in path:
                value = value[hop]
            if type is int and type(value) == str:
                return int(value, 16)
            else:
                return type(value)
        except KeyError:
            logger.debug("Ignoring payload missing metric: %s", ".".join(path))
            return None

    payload = json.loads(payload_str)

    if 'gmtime' in payload:
        timestamp = datetime.datetime.fromtimestamp(payload["gmtime"], tz=datetime.timezone.utc)
    else:
        timestamp = datetime.datetime.utcnow()

    if 'gid' in payload:
        device_gid = _get_metric(["gid"], str)
    else:
        device_gid = None

    data = {
        'tags': {
            'topic': topic,
            'gid': device_gid,
        },
    }

    try:
        if 'elecMtr' in payload:
            assert(_get_metric(["elecMtr", "0702", "03", "00"]) == 0)  # kWh

            electricity_consumption = _get_metric(["elecMtr", "0702", "04", "00"])
            electricity_daily_consumption = _get_metric(["elecMtr", "0702", "04", "01"])
            electricity_weekly_consumption = _get_metric(["elecMtr", "0702", "04", "30"])
            electricity_monthly_consumption = _get_metric(["elecMtr", "0702", "04", "40"])
            electricity_multiplier = _get_metric(["elecMtr", "0702", "03", "01"])
            electricity_divisor = _get_metric(["elecMtr", "0702", "03", "02"])
            electricity_meter = _get_metric(["elecMtr", "0702", "00", "00"])
            electricity_mpan = _get_metric(["elecMtr", "0702", "03", "07"], str)

            data.update({'electricity': {
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
            }})
        elif 'electricitymeter' in payload:
            assert(_get_metric(["electricitymeter", "energy", "import", "mpan"]))
            timestamp = datetime.datetime.strptime(payload["electricitymeter"]["timestamp"], '%Y-%m-%dT%H:%M:%SZ')
            data.update({'electricity': {
                'tags': {
                    'mpan': _get_metric(["electricitymeter", "energy", "import", "mpan"]),
                },
                'metrics': {
                    'draw':                _get_metric(["electricitymeter", "power", "value"], float),
                    'consumption_daily':   _get_metric(["electricitymeter", "energy", "import", "day"], float),
                    'consumption_weekly':  _get_metric(["electricitymeter", "energy", "import", "week"], float),
                    'consumption_monthly': _get_metric(["electricitymeter", "energy", "import", "month"], float),
                    'meter_reading':       _get_metric(["electricitymeter", "energy", "import", "cumulative"], float),
                    'unit_rate':           _get_metric(["electricitymeter", "energy", "import", "price", "unitrate"], float),
                    'standing_charge':     _get_metric(["electricitymeter", "energy", "import", "price", "standingcharge"], float),
                },
            }})
    except AssertionError:
        pass

    try:
        if 'gasMtr' in payload:
            assert(_get_metric(["gasMtr", "0702", "03", "01"]) == 1)  # m3
            assert(_get_metric(["gasMtr", "0702", "03", "12"]) == 0)  # kWh
        
            gas_daily_consumption = _get_metric(["gasMtr", "0702", "0C", "01"])
            gas_weekly_consumption = _get_metric(["gasMtr", "0702", "0C", "30"])
            gas_monthly_consumption = _get_metric(["gasMtr", "0702", "0C", "40"])
            gas_multiplier = _get_metric(["gasMtr", "0702", "03", "01"])
            gas_divisor = _get_metric(["gasMtr", "0702", "03", "02"])
            gas_meter = _get_metric(["gasMtr", "0702", "00", "00"])
            gas_mpan = _get_metric(["gasMtr", "0702", "03", "07"], str)

            data.update({'gas': {
                'tags': {
                    'mpan': gas_mpan,
                },
                'metrics': {
                    'consumption_daily': gas_daily_consumption * gas_multiplier / gas_divisor,
                    'consumption_weekly': gas_weekly_consumption * gas_multiplier / gas_divisor,
                    'consumption_monthly': gas_monthly_consumption * gas_multiplier / gas_divisor,
                    'meter_reading': gas_meter * gas_multiplier / gas_divisor,
                },
            }})
        elif 'gasmeter' in payload:
            assert(_get_metric(["gasmeter", "energy", "import", "mprn"]))
            timestamp = datetime.datetime.strptime(payload["gasmeter"]["timestamp"], '%Y-%m-%dT%H:%M:%SZ')
            data.update({'gas': {
                'tags': {
                    'mpan': _get_metric(["gasmeter", "energy", "import", "mprn"]),
                },
                'metrics': {
                    'meter_reading_kwh':   _get_metric(["gasmeter", "energy", "import", "cumulative"], float),
                    'consumption_daily':   _get_metric(["gasmeter", "energy", "import", "day"], float),
                    'consumption_weekly':  _get_metric(["gasmeter", "energy", "import", "week"], float),
                    'consumption_monthly': _get_metric(["gasmeter", "energy", "import", "month"], float),
                    'meter_reading':       _get_metric(["gasmeter", "energy", "import", "cumulativevol"], float),
                    'unit_rate':           _get_metric(["gasmeter", "energy", "import", "price", "unitrate"], float),
                    'standing_charge':     _get_metric(["gasmeter", "energy", "import", "price", "standingcharge"], float),
                },
            }})
    except AssertionError:
        pass

    if 'electricity' not in data and 'gas' not in data:
        logger.warning("Received a payload without either electricity or gas data")
        return None

    data.update({'timestamp': timestamp})

    return data


def usage_to_datapoints(usage):
    datapoints = []

    for utility in ['electricity', 'gas']:
        if utility in usage:
            datapoints.append({
                "measurement": utility,
                "tags": {**usage['tags'], **usage[utility]['tags']},
                "time": usage['timestamp'].isoformat(),
                "fields": usage[utility]['metrics'],
            })

    return datapoints

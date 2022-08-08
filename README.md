# energy-usage

Realtime energy usage reporting from Bright MQTT feed (SEP) into InfluxDB/VictoriaMetrics. Can be installed and run via pip or docker.

## Configuration

Copy `config.yaml.example` to `config.yaml` and fill in your MQTT login details, and your influx/vm server details.
The config file should be placed into one of the following locations:

* `/etc/energy-usage/config.yaml`
* `~/.config/energy-usage/config.yaml`
* Any dir pointed at by `ENERGY-USAGEDIR` env var

### Local MQTT

Version 0.6 and above supports local MQTT as offered by recent glow CAD firmwares
([announcement blog post](https://medium.com/@joshua.cooper/glow-local-mqtt-f69b776b7af4)).
The data format is subtly different:
- The `gid` label will not be populated
- `unit_rate` and `standing_charge` metrics will be published for each meter type
- `gas_meter_reading_kwh` will also be published

To use with a simple local MQTT broker with no authentication, use a config file like:

```yaml
---
ca_certs: "" # Disables TLS
mqtt:
  server: 10.0.0.1
  port: 1883
  username: "" # Disables auth
  password: "" # Disables auth
  topic: "glow/SENSOR/#"
influx:
  server: 10.0.0.1
  port: 8428
```

And configure the CAD device with mqtt server `10.0.0.1`, port `1883` and topic `glow`

## Pip usage

### Installation

pip install energy-usage

### Run

```bash
energy-usage [--debug] [--noop]
```

* `--debug` enables verbose output about what the script is doing
* `--noop` mode will retrieve stats from mqtt, and show you what would be published to influx but does not actually send anything

## Docker usage

### Build

```bash
docker build -t energy-usage:latest .
```

### Run

```bash
docker run -v config.yaml:/etc/energy-usage/config.yaml energy-usage:latest
```

## Grafana

### Hosted MQTT

`grafana.energy-usage.json` contains an example Grafana dashboard which consumes this data (using the prometheus query interface of VictoriaMetrics).

![Grafana dashboard screenshot](energy-usage-dashboard.png)

Upon import of the dashboard, you will be prompted to select your datasource, and enter your unit and standing charges. These are used to plot the costs of realtime usage data, and the daily/weekly/monthly consumption using accumulated usage statistics by the meters. The dashboard does not currently use live tarrif data, as this is not provided in the Bright MQTT feed.

### Local MQTT

`grafana.energy-usage.local-mqtt.json` contains a similar dashboard for use with the local mqtt data format.

Upon import of the dashboard, you will be prompted to select your datasource. When using local MQTT, the tariff data is included in the published metrics, and the costs displayed are using the live tariff data.

## Tested with:

* Python 3
* VictoriaMetrics 1.40
* Docker 19.03.05
* Nomad 0.12.4

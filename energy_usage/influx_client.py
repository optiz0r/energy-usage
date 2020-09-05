from influxdb import InfluxDBClient


class InfluxClient:
    def __init__(self, server, port, database):
        self.server = server
        self.port = port
        self.database = database

        self.client = InfluxDBClient(
            host=self.server,
            port=self.port,
            database=self.database)

    def write_points(self, body):
        self.client.write_points(body)


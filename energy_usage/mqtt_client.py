import logging

import paho.mqtt.client as mqtt

class MqttClient:
    def __init__(self, server, port, username, password, topic, ca_certs, msg_q):
        self.username = username
        self.password = password
        self.topic = topic
        self.ca_certs = ca_certs
        self.server = server
        self.port = port
        self.msg_q = msg_q

        self.logger = logging.getLogger(__name__)

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def __del__(self):
        self.client.loop_stop()

    def connect(self):
        self.client.username_pw_set(self.username, password=self.password)
        self.client.tls_set(ca_certs=self.ca_certs)
        self.client.connect(self.server, self.port, 60)

    def run(self):
        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        # Other loop*() functions are available that give a threaded interface and a
        # manual interface.
        self.client.loop_start()

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        self.logger.info("Connected with result code " + str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe(self.topic)

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        self.msg_q.put(msg)

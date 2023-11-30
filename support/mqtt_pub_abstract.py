import json
import logging
from datetime import datetime

import paho.mqtt.client as mqtt


class MqttPubAbstract:
    def __init__(self, args, topic):
        self.args = args
        self.topic = topic
        self.client = self.new_client()

    def new_client(self):
        client = mqtt.Client(protocol=mqtt.MQTTv5)
        client.on_connect = self.on_connect
        if self.args.mqtt_port == 8883:
            client.tls_set()
        return client

    def write(self, event, payload=None):
        if not self.client.is_connected():
            self.connect()
        try:
            creation = datetime.now().isoformat()
            json_message = json.dumps({'event': event.name, 'payload': payload, 'creation': creation})
            self.client.publish(self.topic, json_message, retain=False).wait_for_publish(1)
        except Exception as ex:
            logging.info(f"Failed to publish, exception was caught %s", ex)

    def connect(self):
        try:
            self.client.connect(self.args.mqtt_server, port=self.args.mqtt_port)
        except Exception as ex:
            logging.info(f"Failed to connect, exception was caught %s", ex)

    def on_connect(self, _1, _2, _3, rc, _4):
        if not rc == 0:
            raise IOError("Could not connect to mqtt server")

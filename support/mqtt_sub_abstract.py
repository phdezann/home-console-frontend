import json
import logging
import threading
import dateutil.parser

import paho.mqtt.client as mqtt


class MqttSubAbstract:
    def __init__(self, args, killer, topics, callback):
        self.args = args
        self.killer = killer
        self.topics = topics
        self.callback = callback
        self.client = self.new_client()
        self.connect()

    def new_client(self):
        client = mqtt.Client(protocol=mqtt.MQTTv5)
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        if self.args.mqtt_port == 8883:
            client.tls_set()
        return client

    def connect(self):
        self.client.connect(self.args.mqtt_server, port=self.args.mqtt_port)

    def on_connect(self, _1, _2, _3, rc, _4):
        if not rc == 0:
            raise IOError("Could not connect to mqtt server")
        self.subscribe()

    def on_message(self, _1, _2, message):
        topic = message.topic
        json_message = self.decode_utf_8(message)
        data_object = json.loads(json_message)
        event = data_object['event']
        payload = data_object['payload']
        last_touch = self.parse_last_touch(data_object['lastTouch'])
        creation = dateutil.parser.isoparse(data_object['creation'])
        self.callback(topic, event, payload, last_touch, creation)

    def parse_last_touch(self, last_touch):
        if not last_touch:
            return None
        return dateutil.parser.isoparse(last_touch)

    def decode_utf_8(self, message):
        return str(message.payload, "utf-8")

    def read(self):
        try:
            self.connect()
            self.client.loop_forever()
        except Exception as e:
            logging.exception(e)
            self.killer.exit_gracefully()

    def subscribe(self):
        self.client.subscribe(self.to_tuples(self.topics, 0))

    def to_tuples(self, elements, qos):
        result = []
        for element in elements:
            result.append((element, qos))
        return result

    def start_reading_thread(self):
        thread = threading.Thread(target=self.read, args=())
        thread.start()
        return thread

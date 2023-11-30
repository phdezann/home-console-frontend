from support.mqtt_pub_abstract import MqttPubAbstract


class MqttPub(MqttPubAbstract):
    def __init__(self, args, mqtt_topic):
        super().__init__(args, mqtt_topic)

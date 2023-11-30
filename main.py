import logging
from argparse import ArgumentParser

import merciless_killer
from bus.mqtt_topic import WEATHERMAN_INBOX_TOPIC, SCREENWRITER_INBOX_TOPIC
from mqtt_sub import MqttSub
from mqtt_switch_pub import MqttPub
from screen_painter import ScreenPainter
from support.arg_util import str2bool
from touch_sensor import TouchSensor

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

parser = ArgumentParser()
parser.add_argument("--mqtt-server", required=True)
parser.add_argument("--mqtt-port", type=int, default=1883)
parser.add_argument("--touch-switch-gpio", type=int, default=23)
parser.add_argument("--simulate-touch", type=str2bool, nargs='?', const=True, default=False)
args = parser.parse_args()

killer = merciless_killer.MercilessKiller()
weatherman_inbox_pub = MqttPub(args, WEATHERMAN_INBOX_TOPIC)
screen_painter = ScreenPainter()
touch_sensor = TouchSensor(args, weatherman_inbox_pub, screen_painter)
subscribed_topics = [SCREENWRITER_INBOX_TOPIC]
mqtt_subscribe = MqttSub(args, killer, subscribed_topics, screen_painter, touch_sensor)

mqtt_subscribe.start_reading_thread()

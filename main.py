import logging
import sys
from argparse import ArgumentParser

from mqtt.mqtt_monitor import MqttClientMonitor, TerminationStatus
from mqtt.mqtt_sub import MqttSub
from mqtt.mqtt_pub import MqttPub
from screen_painter import ScreenPainter
from arg_util import str2bool
from touch_sensor import TouchSensor
from mqtt_callback import MqttCallback, WEATHERMAN_INBOX_TOPIC, SCREENWRITER_INBOX_TOPIC


def main():
    parser = ArgumentParser()
    parser.add_argument("--mqtt-hostname", required=True)
    parser.add_argument("--mqtt-port", type=int, default=1883)
    parser.add_argument("--touch-switch-gpio", type=int, default=23)
    parser.add_argument("--simulate-touch", type=str2bool, nargs='?', const=True, default=False)
    args = parser.parse_args()

    monitor = MqttClientMonitor()
    screen_painter = ScreenPainter()
    monitor.register_client(screen_painter)
    weatherman_inbox_pub = MqttPub(monitor, args.mqtt_hostname, args.mqtt_port, WEATHERMAN_INBOX_TOPIC, 2)
    touch_sensor = TouchSensor(args, weatherman_inbox_pub, screen_painter)
    monitor.register_client(touch_sensor)
    mqtt_callback = MqttCallback(touch_sensor, screen_painter)
    mqtt_sub = MqttSub(monitor, args.mqtt_hostname, args.mqtt_port, SCREENWRITER_INBOX_TOPIC, 2, mqtt_callback.on_message)

    weatherman_inbox_pub.start()
    mqtt_sub.start()
    logging.info("Mqtt clients are now ready")

    touch_sensor.start_detection()

    termination_status = monitor.wait_for_termination()
    monitor.close_all_clients(termination_status)

    if termination_status == TerminationStatus.NORMAL_TERMINATION:
        sys.exit(0)
    elif termination_status == TerminationStatus.ABNORMAL_TERMINATION:
        sys.exit(1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    main()

import json
import logging

import dateutil
import dateutil.parser

from msg_enum import MsgEnum

WEATHERMAN_INBOX_TOPIC = "weatherman/main/inbox"
SCREENWRITER_INBOX_TOPIC = "screenwriter/main/inbox"


class MqttCallback:
    def __init__(self, touch_sensor, screen_painter):
        self.touch_sensor = touch_sensor
        self.screen_painter = screen_painter

    def on_message(self, payload, topic):
        data_object = json.loads(payload)

        event = data_object['event']
        payload = data_object['payload']
        last_touch = data_object['lastTouch']
        last_touch = self.__parse_last_touch(last_touch)

        if self.touch_sensor.last_touched and last_touch \
                and self.touch_sensor.last_touched != last_touch:
            logging.info("Discarding message %s, it was obsolete", event)
            return

        if topic == SCREENWRITER_INBOX_TOPIC:
            if event == MsgEnum.SHOW_MESSAGE.name:
                self.screen_painter.draw_text(payload)
            if event == MsgEnum.CLEAR_SCREEN.name:
                self.screen_painter.clear()
        else:
            raise Exception("Unsupported topic: " + topic)

    def __parse_last_touch(self, last_touch):
        if not last_touch:
            return None
        return dateutil.parser.isoparse(last_touch)

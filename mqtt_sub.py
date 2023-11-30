import logging

from bus.mqtt_topic import SCREENWRITER_INBOX_TOPIC
from bus.msg_enum import MsgEnum
from support.mqtt_sub_abstract import MqttSubAbstract


class MqttSub(MqttSubAbstract):
    def __init__(self, args, killer, mqtt_topics, screen_painter, touch_sensor):
        super().__init__(args, killer, mqtt_topics, self.callback)
        self.screen_painter = screen_painter
        self.touch_sensor = touch_sensor

    def callback(self, topic, event, payload, last_touch, creation):
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

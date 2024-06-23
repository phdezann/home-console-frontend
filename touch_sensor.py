import json
import logging
import threading
import traceback
from datetime import datetime

import RPi.GPIO as GPIO

from msg_enum import MsgEnum

MINIMUM_INTERVAL_BETWEEN_TOUCH = 200


class TouchSensor:
    def __init__(self, args, weatherman_inbox_pub, screen_painter):
        self.args = args
        self.weatherman_inbox_pub = weatherman_inbox_pub
        self.screen_painter = screen_painter
        self.last_touched = None
        self.active = True

    def is_active(self):
        return self.active

    def close(self, err_msg):
        if self.active:
            logging.warning(f"TouchSensor closed due to '{err_msg}'")
            self.active = False

    def start_simulation(self):
        while True:
            input("Press enter to simulate touch")
            now = datetime.now()
            self.send_msg(now)

    def start_simulation_thread(self):
        thread = threading.Thread(target=self.start_simulation, args=())
        thread.start()
        return thread

    def start_detection(self):
        if self.args.simulate_touch:
            self.start_simulation_thread()
        else:
            try:
                GPIO.setwarnings(False)
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(self.args.touch_switch_gpio, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
                GPIO.add_event_detect(self.args.touch_switch_gpio, GPIO.RISING, self.event_detected, 50)
            except Exception as _:
                logging.error(traceback.format_exc())
                self.active = False

    def event_detected(self, _):
        now = datetime.now()
        if GPIO.input(self.args.touch_switch_gpio) == 1:
            # the thread running with method si called "Dummy-6"
            # it might be a good idea to spin up the make this call
            # but as it is very fast, I don't think it matters much.
            self.send_msg(now)

    def send_msg(self, now):
        if self.last_touch_old_enough(now, MINIMUM_INTERVAL_BETWEEN_TOUCH):
            self.last_touched = now
            self.__publish(MsgEnum.SENSOR_TOUCHED, self.last_touched.isoformat())
            self.screen_painter.start_caterpillar()

    def __publish(self, event, payload=None):
        creation = datetime.now().isoformat()
        json_message = json.dumps({'event': event.name, 'payload': payload, 'creation': creation})
        self.weatherman_inbox_pub.publish(json_message)

    def last_touch_old_enough(self, now, window_size_in_millis):
        if not self.last_touched:
            return True
        delta_in_millis = self.get_difference_in_millis(self.last_touched, now)
        return delta_in_millis > window_size_in_millis

    def get_difference_in_millis(self, from_datetime, to_datetime):
        delta = to_datetime - from_datetime
        return delta.total_seconds() * 1000

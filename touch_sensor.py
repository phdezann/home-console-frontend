import logging
import threading
from datetime import datetime

import RPi.GPIO as GPIO

from bus.msg_enum import MsgEnum

MINIMUM_INTERVAL_BETWEEN_TOUCH = 200


class TouchSensor:
    def __init__(self, args, weatherman_inbox_pub, screen_painter):
        self.args = args
        self.weatherman_inbox_pub = weatherman_inbox_pub
        self.screen_painter = screen_painter
        self.last_touched = None

        if self.args.simulate_touch:
            self.start_simulation_thread()
            return

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.args.touch_switch_gpio, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(self.args.touch_switch_gpio, GPIO.RISING, self.event_detected, 50)

    def start_simulation(self):
        while True:
            input("Press enter to simulate touch")
            now = datetime.now()
            self.send_msg(now)

    def start_simulation_thread(self):
        thread = threading.Thread(target=self.start_simulation, args=())
        thread.start()
        return thread

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
            self.weatherman_inbox_pub.write(MsgEnum.SENSOR_TOUCHED, self.last_touched.isoformat())
            self.screen_painter.start_caterpillar()

    def last_touch_old_enough(self, now, window_size_in_millis):
        if not self.last_touched:
            return True
        delta_in_millis = self.get_difference_in_millis(self.last_touched, now)
        return delta_in_millis > window_size_in_millis

    def get_difference_in_millis(self, from_datetime, to_datetime):
        delta = to_datetime - from_datetime
        return delta.total_seconds() * 1000

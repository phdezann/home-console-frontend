import threading

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106

CATERPILLAR_SIZE = 6


class ScreenPainter:
    def __init__(self):
        serial = i2c(port=1, address=0x3C)
        self.device = sh1106(serial)
        self.screen_lock = threading.Lock()
        self.caterpillar_active_flag_lock = threading.Lock()
        self.caterpillar_active_flag = False
        self.start_caterpillar_drawing_thread()
        self.draw_text(":P")

    def draw_text(self, text):
        self.stop_caterpillar()
        with self.screen_lock:
            with canvas(self.device) as draw:
                lines = text.split("|")
                i = 0
                for line in lines:
                    draw.text((0, i), line, fill="white")
                    if i == 0:
                        i = i + 12
                    else:
                        i = i + 8

    def clear(self):
        self.stop_caterpillar()
        with self.screen_lock:
            with canvas(self.device) as draw:
                draw.rectangle(self.device.bounding_box, outline="black", fill="black")

    def start_caterpillar_drawing(self):
        def draw_text_in_box(text):
            if self.caterpillar_active_flag:
                with self.screen_lock:
                    with canvas(self.device) as draw:
                        draw.rectangle(self.device.bounding_box, outline="white", fill="black")
                        draw.text((48, 25), text, fill="white")

        def draw_return_trip(on_update):
            def update_text(index):
                text = " " * CATERPILLAR_SIZE
                text_as_list = list(text)
                text_as_list[index] = "="
                text = ''.join(text_as_list)
                on_update(text)

            for x_to_right in range(CATERPILLAR_SIZE):
                update_text(x_to_right)
            for x_to_left in range(CATERPILLAR_SIZE - 2, 0, -1):
                update_text(x_to_left)

        while True:
            draw_return_trip(draw_text_in_box)

    def start_caterpillar_drawing_thread(self):
        threading.Thread(target=self.start_caterpillar_drawing, args=()).start()

    def start_caterpillar(self):
        with self.caterpillar_active_flag_lock:
            self.caterpillar_active_flag = True

    def stop_caterpillar(self):
        with self.caterpillar_active_flag_lock:
            self.caterpillar_active_flag = False

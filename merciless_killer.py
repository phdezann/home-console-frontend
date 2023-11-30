import os
import signal


class MercilessKiller:
    def __init__(self):
        self.callbacks = []
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, *args):
        os.kill(os.getpid(), 9)

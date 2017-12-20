
import time


class Timer(object):
    def __init__(self, callback=None):
        self.start = time.time()
        self.callback = callback
    def __enter__(self):
        return self
    def __exit__(self, *args):
        self.duration = time.time() - self.start
        if self.callback:
            self.callback(self.duration)
    def get(self):
        return self.duration

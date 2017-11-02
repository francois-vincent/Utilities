# Copyright 2017 Kosc Telecom

import time


class Timer(object):
    def __init__(self):
        self.start = time.time()
    def __enter__(self):
        return self
    def __exit__(self, *args):
        self.duration = time.time() - self.start
    def get(self):
        return self.duration

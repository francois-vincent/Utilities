# encoding: utf-8

from collections import defaultdict
import sys


class Duplicate(defaultdict):
    def __init__(self, iterator=None):
        defaultdict.__init__(self, list)
        if iterator:
            self.add_iterator(iterator)
    def add_iterator(self, iterator):
        for i, item in enumerate(iterator):
            if item:
                self.add(item, i+1)
        return self
    def add(self, key, val):
        self[key].append(val)
        return self
    def get_dupl(self):
        return [(k, v) for k, v in self.iteritems() if len(v) > 1]


def file_line_iterator(path):
    with open(path, 'r') as f:
        for line in f:
            yield line.strip()


if __name__ == '__main':
    print(Duplicate(file_line_iterator(sys.argv[1])).get_dupl())

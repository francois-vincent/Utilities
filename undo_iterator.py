# coding: utf-8

from collections import deque


class UndoIterator(object):
    """ wraps a plain iterator to offer a two way iterator
        with an optional back depth
    """

    def __init__(self, iterator, depth=5):
        self.iterator = iterator
        self.depth = depth
        self.queue = deque(maxlen=depth+1) if depth > 0 else deque()
        self.back_queue = []

    def __iter__(self):
        return self

    def next(self):
        elt = self.back_queue.pop() if self.back_queue else next(self.iterator)
        self.queue.append(elt)
        return elt

    def prev(self):
        if not self.back_queue:
            self.back_queue.append(self.queue.pop())
        elt = self.queue.pop()
        self.back_queue.append(elt)
        return elt
    back = undo = prev

    def cur(self):
        return self.queue[-1]


if __name__ == '__main__':
    ui = UndoIterator(iter('ABCDE'))
    for i, x in enumerate(ui):
        print(i, x)
        if i == 2:
            print("current: %s" % ui.cur())
        if i == 3:
            print("undo:    %s" % ui.undo())
        if i == 6:
            print("undo:    %s" % ui.undo())
            print("undo:    %s" % ui.undo())

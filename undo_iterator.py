# coding: utf-8

from collections import deque


class UndoIterator(object):
    """ wraps a plain iterator to offer a two way iterator
        with an optional back depth
    """
    def __init__(self, iterator, depth=5):
        self._iterator = iterator
        self._queue = deque(maxlen=depth+1) if depth > 0 else []
        self._back_queue = []
        self._lock_repeat = False  # control consecutive executions of repeat()
        self.index = 0  # simulate enumerate() on the go

    def __iter__(self):
        return self

    def next(self):
        self._lock_repeat = False
        elt = self._back_queue.pop() if self._back_queue else next(self._iterator)
        self._queue.append(elt)
        self.index += 1
        return elt

    def repeat(self):
        if not self._lock_repeat:
            self._lock_repeat = True
            self._back_queue.append(self._queue.pop())
            self.index -= 1

    def prev(self):
        self.repeat()
        elt = self._queue.pop()
        self._back_queue.append(elt)
        self.index -= 1
        return elt

    def can_undo(self):
        return len(self._queue) > 1

    def cur(self):
        return self._queue[-1]


if __name__ == '__main__':
    ui = UndoIterator(iter('ABCDE'))
    for i, x in enumerate(ui):
        print(i, x, ui.index)
        if i == 2:
            print("current: %s" % ui.cur())
        if i == 3:
            print("undo:    %s" % ui.prev())
        if i == 6:
            print("undo:    %s" % ui.prev())
            print("undo:    %s" % ui.prev())
        if 7 <= i <= 8:
            print("repeat")
            ui.repeat()

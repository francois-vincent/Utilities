# coding: utf-8

from collections import deque


class UndoIterator(object):
    """ wraps a plain iterator to offer a two way iterator
        with an optional back depth
    """
    def __init__(self, iterator, depth=5):
        self.iterator = iterator
        self.queue = deque(maxlen=depth+1) if depth > 0 else []
        self.back_queue = []
        self.index = 0  # simulate enumerate() on the go

    def __iter__(self):
        return self

    def next(self):
        elt = self.back_queue.pop() if self.back_queue else next(self.iterator)
        self.queue.append(elt)
        self.index += 1
        return elt

    def repeat(self):
        self.back_queue.append(self.queue.pop())
        self.index -= 1

    def prev(self):
        self.repeat()
        elt = self.queue.pop()
        self.back_queue.append(elt)
        self.index -= 1
        return elt

    def can_undo(self):
        return len(self.queue) > 1

    def cur(self):
        return self.queue[-1]


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

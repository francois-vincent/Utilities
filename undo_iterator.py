# coding: utf-8

from collections import deque


class UndoIterator(object):
    """ wraps a plain iterator to offer a two way iterator
        with a controlled back step depth
    """
    def __init__(self, iterator, depth=2, start_index=0):
        self._iterator = iterator
        self._queue = deque(maxlen=depth+1) if depth > 0 else []
        self._back_queue = []
        self.index = start_index - 1  # simulate enumerate() on the go

    def __iter__(self):
        return self

    def __len__(self):
        return len(self._queue)

    def next(self):
        elt = self._back_queue.pop() if self._back_queue else next(self._iterator)
        self._queue.append(elt)
        self.index += 1
        return elt

    def prev(self):
        elt = self._queue.pop()
        self._back_queue.append(elt)
        self.index -= 1
        return elt

    def cur(self):
        return self._queue[-1]


if __name__ == '__main__':
    ui = UndoIterator(iter('ABCDE'))
    for i, x in enumerate(ui):
        print(i, x, ui.index)
        if i == 2:
            print("current: %s" % ui.cur())
        if i == 3:  # a single prev() will replay the last step
            print("undo:    %s" % ui.prev())
        if i == 5:  # to really undo and get the step before the last one, call prev() twice
            print("undo:    %s" % ui.prev())
            print("undo:    %s" % ui.prev())

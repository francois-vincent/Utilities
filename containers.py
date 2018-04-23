# coding: utf-8


class CyclicRemovable(object):
    """ Implements a cyclic iterator over a finite set of objects
        where you can remove objects while iterating and the iterator will
        automatically skip removed objects.
        It is efficient in the sense that there is no more iteration than strictly required
        by using a kind of simply linked list that skips dropped elements.
    """

    class Dropped(object):
        pass

    def __init__(self, iterable, iterator=False, debug=False):
        self.index = 0
        if iterator:
            self.elements = list(iter(it) for it in iterable)
        else:
            self.elements = list(iterable)
        self.length = len(self.elements)
        self.indexes = range(1, self.length)  # list of indexes of next element
        self.indexes.append(0)
        self.debug = debug

    def remove(self, index):
        if self.debug:
            print("####### remove %d" % index)
        assert self.length  # can't remove if list is empty
        assert self.elements[index] is not self.Dropped  # can't remove same element twice
        if self.length == 1:
            assert index == self.index
        else:
            self.elements[index] = self.Dropped
            if self.index == index:
                # forward index such that current index is not a dropped element
                next_element, next_index = self.elements[index], self.indexes[index]
                good_index = next_index
                while next_element is self.Dropped:
                    good_index = next_index
                    next_element, next_index = self.elements[next_index], self.indexes[next_index]
                self.index = good_index
        self.length -= 1
        return self

    def __len__(self):
        return self.length

    def __iter__(self):
        return self

    def next(self):
        if self.length:
            # return next element and update chain of non dropped elements
            element, next_index = self.elements[self.index], self.indexes[self.index]
            good_index = next_index
            next_element, next_next_index = self.elements[next_index], self.indexes[next_index]
            while next_element is self.Dropped:
                good_index = next_next_index
                next_element, next_next_index = self.elements[next_next_index], self.indexes[next_next_index]
            if next_index != good_index:
                # change index of current element to point on next non dropped element
                self.indexes[self.index] = good_index
            index, self.index = self.index, good_index
            return index, element
        raise StopIteration()


if __name__ == '__main__':
    cr = CyclicRemovable('ABCDE', debug=True)
    for i, x in enumerate(cr):
        print(i, x)
        if i == 1:
            cr.remove(1)
        if i == 5:
            cr.remove(3)
        if i == 6:
            cr.remove(2)
            cr.remove(4)
        if i == 9:
            cr.remove(0)

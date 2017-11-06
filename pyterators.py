# -*- coding: utf-8 -*-

import itertools


def close_product(*sequences):
    """ returns a sequence over the cartesian product of parameter sequences but,
        unlike itertools.product, orders the resulting sequence in increasing
        distance order wrt origin, in terms of indices, e.g. :
        CloseProduct((0,1,2), (0,1,2)) will return:
        [(0,0), (0,1), (1,0), (0,2), (1,1), (2,0), (1,2), (2,1), (2,2)]
    """
    indices = [range(len(x)) for x in sequences]   # indices of each sequence, in a new sequence
    product = list(itertools.product(*indices))
    product.sort(key=sum)                          # sort cartesian product according to sum of indices
    return [[sequences[i][j] for i, j in enumerate(x)] for x in product]  # restore sequences from indices


def chunk_iter(iterable, chunk_size):
    assert chunk_size > 1
    iterator = iter(iterable)
    while True:
        n = next(iterator)
        yield itertools.chain((n,), itertools.islice(iterator, chunk_size - 1))


def first(iterable, condition, default=None):
    """ return the first element in an iterable that satisfies the condition
    """
    return next((x for x in iterable if condition(x)), default)


if __name__ == '__main__':
    for i in close_product((0, 1, 2, 3), (0, 1), (0, 1)):
        print(i)
    for i in close_product(('a', 'b', 'c', 'd'), ('a', 'b'), ('a', 'b')):
        print(i)

    for x in chunk_iter(xrange(10), 3):
        print(tuple(x))

    assert tuple(''.join(x) for x in chunk_iter('abcdefghij', 3)) == ('abc', 'def', 'ghi', 'j')

    assert first(xrange(5), lambda x: x > 3) == 4
    assert first(xrange(5), lambda x: x > 4) is None

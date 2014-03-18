# -*- coding: utf-8 -*-

import itertools


def CloseProduct(*sequences):
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


if __name__ == '__main__':
    for i in CloseProduct(('a','b','c','d'), ('a','b'), ('a','b')):
        print i

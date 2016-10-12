# coding: utf-8

from __future__ import print_function


def infinite_integer(i=0, step=1):
    """ yields an infinite integer suite with an optional start and step
    :param i: start, default 0
    :param step: default 1
    """
    while True:
        yield i
        i += step


def integer_filter(*a):
    """ yields an infinite filtered integer suite
    :param a: an optional sequence of integers whose multiples will be filtered out
              if empty, will yield primes
    """
    if a:
        def f():
            divs = [[x, x] for x in a]
            i = 1
            while True:
                yield i
                while True:
                    i += 1
                    hit = False
                    for div in divs:
                        if i == div[1]:
                            div[1] += div[0]
                            hit = True
                    if not hit:
                        break
    else:
        def f():
            divs = [[2, 4]]
            i = 2
            while True:
                yield i
                while True:
                    i += 1
                    j, hit = i, False
                    for div in divs:
                        if i == div[1]:
                            div[1] += div[0]
                            hit = True
                            # small optimization for large numbers
                            j /= div[0]
                            if j == 1:
                                break
                    if not hit:
                        divs.append([i, i + i])
                        break
    return f()


if __name__ == '__main__':
    ii = infinite_integer()
    for n in xrange(30):
        print(next(ii), end=' ')
    print('\n')

    ii = infinite_integer(5, 5)
    for n in xrange(30):
        print(next(ii), end=' ')
    print('\n')

    # this will filter out all multiples of 2 and 3
    inf = integer_filter(2, 3)
    for n in xrange(30):
        print(next(inf), end=' ')
    print('\n')

    # this will print first primes
    inf = integer_filter()
    for n in xrange(30):
        print(next(inf), end=' ')
    print('\n')

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
    """ yields an infinite integer suite filtered by divisors
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
            yield 2
            divs = [[3, 9]]
            i = 3
            while True:
                yield i
                while True:
                    i += 2
                    j, hit = i, False
                    for div in divs:
                        if i == div[1]:
                            d = div[0]
                            div[1] += d + d
                            hit = True
                            # optimization for large numbers
                            j /= d
                            if j == 1:
                                break
                    if not hit:
                        divs.append([i, 3 * i])
                        break
    return f()


def it_window(it, a, b=None):
    """ yields a window of values out of an iterator
    :param it: an iterator
    :param a: if b is None, a is the number of values yielded
    :param b: if not None, b is the number of values yielded
              and a is the number of values skipped.
    Notice: use 'from itertools import islice' instead
    """
    if b is None:
        b, a = a, 0
    for _ in xrange(a):
        next(it)
    for _ in xrange(b):
        yield next(it)


def it_binary(it, op, inv=False):
    """ yields the result of a binary operator between consecutive values of an iterator
    :param it: an iterator
    :param op: a binary operator
    :param inv: if inv is True, the operands are inverted
    """
    a = next(it)
    while True:
        b = next(it)
        yield op(b, a) if inv else op(a, b)
        a = b


if __name__ == '__main__':
    # slice of 10 first integers
    assert list(it_window(infinite_integer(), 10)) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    # slice of 3 integers after 10 first
    assert list(it_window(infinite_integer(), 10, 3)) == [10, 11, 12]

    # slice of 10 first multiples of 5
    assert list(it_window(infinite_integer(5, 5), 10)) == [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]

    # slice of 20 first integers not multiple of 2 and 3
    assert list(it_window(integer_filter(2, 3), 20)) == [1, 5, 7, 11, 13, 17, 19, 23, 25, 29, 31, 35, 37,
                                                         41, 43, 47, 49, 53, 55, 59]

    # a slice can be applied on a shorter generator
    assert list(it_window(iter(xrange(5)), 10)) == [0, 1, 2, 3, 4]

    # check first 200 primes
    first_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101,
            103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199,
            211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317,
            331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443,
            449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577,
            587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701,
            709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839,
            853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983,
            991, 997, 1009, 1013, 1019, 1021, 1031, 1033, 1039, 1049, 1051, 1061, 1063, 1069, 1087, 1091, 1093,
            1097, 1103, 1109, 1117, 1123, 1129, 1151, 1153, 1163, 1171, 1181, 1187, 1193, 1201, 1213, 1217, 1223]
    assert list(it_window(integer_filter(), 200)) == first_primes

    # check 5 primes after 1000th
    assert list(it_window(integer_filter(), 1000, 5)) == [7927, 7933, 7937, 7949, 7951]

    from operator import add, sub
    assert list(it_binary(iter(xrange(7)), add)) == [1, 3, 5, 7, 9, 11]

    # check the 50 first consecutive primes differences
    primes_diff = [1, 2, 2, 4, 2, 4, 2, 4, 6, 2, 6, 4, 2, 4, 6, 6, 2, 6, 4, 2, 6, 4, 6, 8, 4, 2, 4, 2, 4, 14, 4, 6, 2,
                   10, 2, 6, 6, 4, 6, 6, 2, 10, 2, 4, 2, 12, 12, 4, 2]
    assert list(it_binary(it_window(integer_filter(), 50), sub, inv=True)) == primes_diff

    # check the max gap between 2000 first primes
    assert max(it_binary(it_window(integer_filter(), 2000), sub, inv=True)) == 44

    print("All tests OK !")

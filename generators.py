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
                            # small optimization for large numbers
                            j /= d
                            if j == 1:
                                break
                    if not hit:
                        divs.append([i, 3 * i])
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
    inf = integer_filter()
    assert [next(inf) for _ in xrange(200)] == first_primes

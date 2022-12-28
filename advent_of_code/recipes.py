from typing import Iterable


def trace_points(a: int, b: int) -> Iterable[int]:
    """Returns the integers in between a and b

    >>> list(trace_points(-2, -6))
    [-2, -3, -4, -5, -6]

    :param a: Start value, inclusive
    :param b: End value, inclusive
    :return: An `Iterable` of all values in between a and b inclusive
    """

    inc = 1 if b > a else -1
    while a != b:
        yield a
        a += inc

    yield a

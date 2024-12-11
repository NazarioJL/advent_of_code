from math import log10, ceil

import pytest
from functools import cache

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data


YEAR = 2024
DAY = 11


def num_digits(n: int) -> int:
    """
    Return the number of digits in n. This is my own ghetto function, and I'm sure
    there's a better way to do this.
    """
    log_ = log10(n)
    if log_ == int(log_):
        return int(log_) + 1
    else:
        return ceil(log_)


def blink(stone: int) -> int | tuple[int, int]:
    if stone == 0:
        return 1
    d_count = num_digits(stone)
    if d_count % 2 == 0:
        tens = 10 ** (d_count // 2)
        left = stone // tens
        right = stone - (left * tens)
        return left, right
    else:
        return stone * 2024


def blink_n(stones: list[int], blinks: int) -> list[int]:
    old_stones = stones
    new_stones = []

    for _ in range(blinks):
        for stone in old_stones:
            res = blink(stone)
            if isinstance(res, tuple):
                new_stones.append(res[0])
                new_stones.append(res[1])
            else:
                new_stones.append(res)

        old_stones = new_stones
        new_stones = []

    return old_stones


def count_blinks(stones: list[int], blinks: int) -> int:
    @cache
    def count_rec(s: int, rem: int) -> int:
        if rem == 0:
            return 1
        else:
            if s == 0:
                return count_rec(1, rem - 1)
            else:
                d_count = num_digits(s)
                if d_count % 2 == 0:
                    tens = 10 ** (d_count // 2)
                    left = s // tens
                    right = s - (left * tens)
                    return count_rec(left, rem - 1) + count_rec(right, rem - 1)
                else:
                    return count_rec(s * 2024, rem - 1)

    return sum(count_rec(stone, blinks) for stone in stones)


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    stones = [int(n) for n in s.strip().split(" ")]
    result = blink_n(stones, 25)
    part_1 = len(result)
    part_2 = count_blinks(stones, 75)

    return part_1, part_2


TEST_INPUT = """\
125 17
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, (55312, 65601038650482)),),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


@pytest.mark.parametrize(
    ("stone", "expected"),
    [
        (1, 2024),
        (0, 1),
        (99, (9, 9)),
        (999, 2021976),
        (1000, (10, 0)),
        (9876, (98, 76)),
    ],
)
def test_blink(stone: int, expected: int | tuple[int, int]) -> None:
    assert blink(stone) == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))

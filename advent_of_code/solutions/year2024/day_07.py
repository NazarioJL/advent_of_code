from math import log10
from operator import mul, add
from typing import Callable, Optional

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2024
DAY = 7


def combine(left: int, right: int) -> int:
    """Combines left number with right number
    >>> combine(1, 2)
    12
    >>> combine(123, 456)
    123456
    """

    if left < 0 or right < 0:
        raise ValueError("Only accepts positive numbers")
    return 10 ** (int(log10(right)) + 1) * left + right  # type: ignore


def can_compute_test(
    test: int, operands: list[int], operations: list[Callable[[int, int], int]]
) -> int:
    def compute_rec(curr: Optional[int], idx: int) -> bool:
        if idx == len(operands):
            return curr == test
        elif idx == 0:
            return compute_rec(operands[0], idx + 1)
        else:
            assert curr
            return any(
                compute_rec(func(curr, operands[idx]), idx + 1) for func in operations
            )

    if compute_rec(None, 0):
        return test
    else:
        return 0


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    def line_to_args(line: str) -> tuple[int, ...]:
        test_value, nums = line.split(":")
        return int(test_value), *(int(n) for n in nums.strip().split(" "))

    entries = [line_to_args(line) for line in s.splitlines()]

    part_1 = sum(
        can_compute_test(test_val, [*ops], [add, mul]) for test_val, *ops in entries
    )
    part_2 = sum(
        can_compute_test(test_val, [*ops], [add, combine, mul])
        for test_val, *ops in entries
    )

    return part_1, part_2


TEST_INPUT = """\
190: 10 19
3267: 81 40 27
83: 17 5
156: 15 6
7290: 6 8 6 15
161011: 16 10 13
192: 17 8 14
21037: 9 7 18 13
292: 11 6 16 20
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, (3749, 11387)),),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))

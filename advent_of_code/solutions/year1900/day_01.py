import operator
from functools import reduce

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.parsers import parse_ints
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data


YEAR = 1900
DAY = 1


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    nums = parse_ints(s)
    return sum(nums), reduce(operator.mul, nums, 1)


TEST_INPUT = """\
1
2
3
4
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, ""),),
)
def test_solve(input_s: str, expected: str) -> None:
    assert solve(input_s).as_tuple() == (10, 24)


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
    print(aoc.count_solutions())
    import os

    print(os.getenv("PYTHONPATH"))

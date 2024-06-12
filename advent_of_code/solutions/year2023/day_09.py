import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.exceptions import SolutionNotImplementedError
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data


YEAR = 2023
DAY = 9


def differentiate(nums: list[int]) -> list[int]:
    return [nums[i] - nums[i - 1] for i in range(1, len(nums))]


def parse_input(s: str) -> list[list[int]]:
    for line in s.splitlines():
        yield [int(n) for n in line.split()]


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    for nums in parse_input(s):
        diff_list = []
        diff = differentiate(nums)
        if any(diff):
            diff_list.append(diff[-1])
        else:
            break


TEST_INPUT = """\
0 3 6 9 12 15
1 3 6 10 15 21
10 13 16 21 30 45
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, ()),),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))

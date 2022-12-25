import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.exceptions import SolutionNotImplementedError
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data


YEAR = 2022
DAY = 25


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    raise SolutionNotImplementedError


TEST_INPUT = """\
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, ()),),
)
def test_solve(input_s: str, expected: str) -> None:
    assert solve(input_s).as_tuple() == ()


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))

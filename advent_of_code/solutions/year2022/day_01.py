import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data


YEAR = 2022
DAY = 1


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    totals = [
        sum(int(num_s) for num_s in group.splitlines()) for group in s.split("\n\n")
    ]
    totals.sort(reverse=True)
    return totals[0], sum(totals[0:3])


TEST_INPUT = """\
1000
2000
3000

4000

5000
6000

7000
8000
9000

10000

"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, (24000, 45000)),),
)
def test_solve(input_s: str, expected: tuple[int, int]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))

from itertools import product

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2024
DAY = 25


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    scms = [
        (ls[0][0], [sum(ls[r][c] == "#" for r in range(7)) for c in range(5)])
        for scm in s.split("\n\n")
        if (ls := scm.splitlines())
    ]
    return sum(
        all((a + b) <= 7 for a, b in zip(l, k))
        for l, k in product(
            (scm[1] for scm in scms if scm[0] == "#"),
            ((scm[1] for scm in scms if scm[0] == ".")),
        )
    ), 0


TEST_INPUT = """\
#####
.####
.####
.####
.#.#.
.#...
.....

#####
##.##
.#.##
...##
...#.
...#.
.....

.....
#....
#....
#...#
#.#.#
#.###
#####

.....
.....
#.#..
###..
###.#
###.#
#####

.....
.....
.....
#....
#.#..
#.#.#
#####
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    [
        (TEST_INPUT, (3, 0)),
    ],
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))

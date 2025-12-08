from functools import cache

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data


YEAR = 2025
DAY = 7


def part_2(s: str) -> int:
    rows = s.splitlines()
    start = 0
    for col, char in enumerate(rows[0]):
        if char == "S":
            start = col
            break
    col_count = len(rows[0])

    @cache
    def split(r, c) -> int:
        if r == len(rows) or c == col_count or c == -1:
            return 1
        else:
            if rows[r][c] == "^":
                return split(r + 1, c - 1) + split(r + 1, c + 1)
            else:
                return split(r + 1, c)

    return split(0, start)


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    rows = s.splitlines()
    # find starting point
    tachyons: set[int] = set()
    for col, char in enumerate(rows[0]):
        if char == "S":
            tachyons.add(col)
            break
    splits = 0
    for row in rows[1:]:
        for col, char in enumerate(row):
            if char == "^" and col in tachyons:
                # split col
                tachyons.remove(col)
                tachyons.add(col + 1)
                tachyons.add(col - 1)
                splits += 1

    # start from the bottom

    return splits, part_2(s)


TEST_INPUT = """\
.......S.......
...............
.......^.......
...............
......^.^......
...............
.....^.^.^.....
...............
....^.^...^....
...............
...^.^...^.^...
...............
..^...^.....^..
...............
.^.^.^.^.^...^.
...............
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    [
        (TEST_INPUT, (21, 40)),
    ],
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))

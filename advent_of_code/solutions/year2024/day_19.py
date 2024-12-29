from functools import cache

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2024
DAY = 19


def can_make_design(design: str, patterns: set[str]) -> bool:
    @cache
    def can_make_rec(index: int) -> bool:
        if index == len(design) or design[index:] in patterns:
            return True
        for pattern in patterns:
            if design[index : index + len(pattern)] == pattern:
                if can_make_rec(index + len(pattern)):
                    return True
                continue
        return False

    return can_make_rec(0)


def count_ways(design: str, patterns: set[str]) -> int:
    memo = [-1] * len(patterns)

    def count_ways_rec(index: int) -> int:
        if memo[index] != -1:
            return memo[index]
        if index > len(design):
            return 0
        if index == len(design):
            return 1
        result = 0
        for pattern in patterns:
            if design.startswith(pattern, index):
                result += count_ways_rec(index + len(pattern))

        memo[index] = result
        return result

    return count_ways_rec(0)


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    patterns_str, designs_str = s.split("\n\n")

    patterns = {p.strip() for p in patterns_str.split(",")}
    designs = designs_str.splitlines()

    part_1 = sum(int(can_make_design(design, patterns)) for design in designs)
    part_2 = sum(count_ways(design, patterns) for design in designs)

    return part_1, part_2


TEST_INPUT = """\
r, wr, b, g, bwu, rb, gb, br

brwrr
bggr
gbbr
rrbgbr
ubwu
bwurrg
brgr
bbrgwb
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    [
        (TEST_INPUT, (6, 16)),
    ],
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))

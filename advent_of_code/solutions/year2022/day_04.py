from typing import Iterable
from typing import TypeAlias

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data


YEAR = 2022
DAY = 4

Range: TypeAlias = tuple[int, int]
Pair: TypeAlias = tuple[Range, Range]


def parse_input(s: str) -> Iterable[Pair]:
    def parse_range(pair_s: str) -> Range:
        a, b = pair_s.split("-")
        return int(a), int(b)

    for line in s.splitlines():
        r_1, r_2 = line.split(",")
        yield parse_range(r_1), parse_range(r_2)


def inside(r1: Range, r2: Range) -> bool:
    a1, b1 = r1
    a2, b2 = r2

    assert a1 <= b1
    assert a2 <= b2

    return a1 >= a2 and b1 <= b2


def inside_any(r1: Range, r2: Range) -> bool:
    return inside(r1, r2) or inside(r2, r1)


def overlaps(r1: Range, r2: Range) -> bool:
    a1, b1 = r1
    a2, b2 = r2

    assert a1 <= b1
    assert a2 <= b2

    return (a2 <= a1 <= b2) or (a2 <= b1 <= b2) or inside_any(r1, r2)


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    pairs = list(parse_input(s))
    part_1 = sum(inside_any(r1, r2) for r1, r2 in pairs)
    part_2 = sum(overlaps(r1, r2) for r1, r2 in pairs)

    return part_1, part_2


TEST_INPUT = """\
2-4,6-8
2-3,4-5
5-7,7-9
2-8,3-7
6-6,4-6
2-6,4-8
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, (2, 4)),),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))

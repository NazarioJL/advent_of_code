from functools import cmp_to_key
from typing import Iterable
from typing import TypeAlias

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data


YEAR = 2022
DAY = 13

TInput: TypeAlias = list["TInput"] | int


def compare(left: TInput, right: TInput) -> int:
    if isinstance(left, int) and isinstance(right, int):
        if left < right:
            return 1
        elif left > right:
            return -1
        else:
            return 0
    elif isinstance(left, list) and isinstance(right, list):
        if len(left) == 0 and len(right) == 0:  # [] and [] are equivalent
            return 0
        tmp = 1
        for i, e in enumerate(left):
            if i >= len(right):
                # Right side ran out of elements
                return -1  # Not in right order
            tmp = compare(e, right[i])
            if tmp != 0:
                return tmp
        if len(left) < len(right):
            return 1
        else:
            return tmp
    else:  # mixed case
        if isinstance(left, int):
            return compare([left], right)
        else:
            return compare(left, [right])


def parse_input(s: str) -> Iterable[tuple[TInput, TInput]]:
    for chunk in s.split("\n\n"):
        left, right = chunk.splitlines()
        yield eval(left), eval(right)


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    packets = list(parse_input(s))

    part_1 = sum(
        idx + 1
        for idx, res in enumerate([compare(l, r) for l, r in packets])
        if res == 1
    )

    all_packets = [packet for pair in packets for packet in pair]
    all_packets.append([[2]])
    all_packets.append([[6]])
    all_packets.sort(key=cmp_to_key(compare), reverse=True)

    idx_1 = -1
    idx_2 = -1

    for i, p in enumerate(all_packets):
        if p == [[2]]:
            idx_1 = i
        if p == [[6]]:
            idx_2 = i

    assert idx_1 >= 0
    assert idx_2 >= 0

    part_2 = (idx_1 + 1) * (idx_2 + 1)

    return part_1, part_2


TEST_INPUT = """\
[1,1,3,1,1]
[1,1,5,1,1]

[[1],[2,3,4]]
[[1],4]

[9]
[[8,7,6]]

[[4,4],4,4]
[[4,4],4,4,4]

[7,7,7,7]
[7,7,7]

[]
[3]

[[[]]]
[[]]

[1,[2,[3,[4,[5,6,7]]]],8,9]
[1,[2,[3,[4,[5,6,0]]]],8,9]
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, (13, 140)),),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    (
        ([1, 2, 3], [1, 2, 3], 0),
        ([1, 2, 3], [1, 2, 3, 4], 1),
        ([1, 2, 3], [1, 2], -1),
        ([1, 3, 3], [1, 2], -1),
        ([1, 1, 3, 1, 1], [1, 1, 5, 1, 1], 1),
        ([[1], [2, 3, 4]], [[1], 4], 1),
        ([9], [[8, 7, 6]], -1),
        ([[4, 4], 4, 4], [[4, 4], 4, 4, 4], 1),
        ([7, 7, 7, 7], [7, 7, 7], -1),
        ([], [3], 1),
        ([[[]]], [[]], -1),
        ([1, [2, [3, [4, [5, 6, 7]]]], 8, 9], [1, [2, [3, [4, [5, 6, 0]]]], 8, 9], -1),
    ),
)
def test_compare(left: TInput, right: TInput, expected: int) -> None:
    assert compare(left, right) == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))

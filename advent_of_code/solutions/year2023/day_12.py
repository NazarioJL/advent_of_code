from functools import cache
from typing import Iterable

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2023
DAY = 12


def find_arrangements(record: str, config: list[int]) -> int:  # noqa: C90
    @cache
    def rec(ri: int, ci: int) -> int:
        if ci == len(config):
            # No more groups to match
            if "#" in record[ri:]:
                return 0
            else:
                # All that is left, is either "." or a "?" acting as "."
                return 1
        else:
            while ri < len(record) and record[ri] == ".":  # Find next start
                ri += 1
            if ri >= len(record):
                return 0
            if ri > 0 and record[ri - 1] == "#":
                # We have to be at the beginning or have space ("?"|".") before current
                # group
                return 0
            result = 0

            if record[ri] == "?":
                # Take ? as "." and find arrangements w/o choosing current pos as #
                result += rec(ri + 1, ci)

            group_size = config[ci]
            curr_group = record[ri : ri + group_size]
            if len(curr_group) < group_size:
                return result
            if "." in curr_group:
                # Can't have empty spaces in group
                return result
            if record[ri + group_size : ri + group_size + 1] == "#":
                # Can't have # right next to current group
                return result

            result += rec(ri + group_size + 1, ci + 1)

            return result

    return rec(0, 0)


def parse_input(s: str) -> Iterable[tuple[str, list[int]]]:
    for line in s.splitlines():
        record, config = line.split()
        yield record, [int(c) for c in config.split(",")]


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    items = list(parse_input(s))

    part_1 = sum(find_arrangements(record, config) for (record, config) in items)
    part_2 = sum(
        find_arrangements("?".join([record] * 5), config * 5)
        for (record, config) in items
    )

    return part_1, part_2


TEST_INPUT = """\
???.### 1,1,3
.??..??...?##. 1,1,3
?#?#?#?#?#?#?#? 1,3,1,6
????.#...#... 4,1,1
????.######..#####. 1,6,5
?###???????? 3,2,1
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, (21, 525152)),),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


@pytest.mark.parametrize(
    ("record", "config", "expected"),
    (
        ("??.#.###", [1, 1, 3], 2),
        (".??.#.###?", [1, 1, 3], 2),
        ("#.#.###", [1, 1, 3], 1),
        ("#.#.###..", [1, 1, 3], 1),
        (".#.#.###..", [1, 1, 3], 1),
        ("???.###", [1, 1, 3], 1),
        ("??.###", [1, 1, 3], 0),
        (".??.?#", [1, 1], 2),
        (".?#", [1], 1),
        (".??...?##.", [1, 3], 2),
        (".??..??...?##.", [1, 1, 3], 4),
        ("?#?#?#?#?#?#?#?", [1, 3, 1, 6], 1),
        ("????.#...#...", [4, 1, 1], 1),
        ("????.######..#####.", [1, 6, 5], 4),
        ("?###????????", [3, 2, 1], 10),
    ),
)
def test_find_arrangements(record: str, config: list[int], expected: int) -> None:
    actual = find_arrangements(record, config)

    assert actual == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))

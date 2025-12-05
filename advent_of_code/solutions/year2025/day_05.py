from bisect import bisect_right
from operator import itemgetter

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2025
DAY = 5


def parse_input(s: str) -> tuple[list[tuple[int, int]], list[int]]:
    section_1, section_2 = s.split("\n\n")
    fresh_ingredient_ranges = [
        (int(parts[0]), int(parts[1]))
        for line in section_1.splitlines()
        if (parts := line.split("-"))
    ]
    available_ingredients = [int(line) for line in section_2.splitlines()]

    return fresh_ingredient_ranges, available_ingredients


def merge_ranges(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    # If list is empty or has only one interval, return as is
    if not intervals or len(intervals) == 1:
        return intervals

    # Sort intervals based on start time
    intervals.sort(key=itemgetter(0))

    result = []
    current = list(intervals[0])

    for next_interval in intervals[1:]:
        # If current interval overlaps with next interval
        if current[1] >= next_interval[0]:
            # Merge by taking the maximum of end times
            current[1] = max(current[1], next_interval[1])
        else:
            # No overlap, add current to result and move to next
            result.append(tuple(current))
            current = list(next_interval)

    # Add the last interval
    result.append(tuple(current))
    return result


def get_fresh_ingredients(
    ranges: list[tuple[int, int]], available_ingredients: list[int]
) -> list[int]:
    """Gets all available ingredients that are within one of the ranges

    :param ranges: list of non-overlapping ranges, sorted by start
    :param available_ingredients: list of available ingredients
    :return: list of fresh ingredients (those that are within a range)
    """
    fresh_ingredients = []
    for item in available_ingredients:
        idx = bisect_right(ranges, item, key=itemgetter(0))
        if idx == 0:
            continue
        else:
            test_s, test_e = ranges[idx - 1]
            if test_s <= item <= test_e:
                fresh_ingredients.append(item)

    return fresh_ingredients


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    parsed_ranges, available_ingredients = parse_input(s)
    merged_ranges = merge_ranges(parsed_ranges)
    part_1 = get_fresh_ingredients(merged_ranges, available_ingredients)
    part_2 = sum(e - s + 1 for s, e in merged_ranges)
    return len(part_1), part_2


TEST_INPUT = """\
3-5
10-14
16-20
12-18

1
5
8
11
17
32
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    [
        (TEST_INPUT, (3, 14)),
    ],
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))

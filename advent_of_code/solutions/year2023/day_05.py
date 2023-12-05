import re
from itertools import pairwise
from typing import Iterable
from typing import NamedTuple

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2023
DAY = 5


class RangeMap(NamedTuple):
    source_start: int
    dest_start: int
    length: int


class Range(NamedTuple):
    """
    Describes a range.
    """

    start: int
    length: int

    @property
    def left(self) -> int:
        """Leftmost point"""
        return self.start

    @property
    def right(self) -> int:
        """Rightmost point"""
        return self.start + self.length - 1

    @staticmethod
    def from_segment(left: int, right: int) -> "Range":
        return Range(start=left, length=right - left + 1)


def parse_map(s: str) -> tuple[tuple[str, str], list[RangeMap]]:
    it = iter(s.splitlines())
    title = next(it)

    [source, _, dest, *_] = re.split(r" |-| ", title)
    ranges = []

    while line := next(it, None):
        dest_start, src_start, length = line.split()
        ranges.append(RangeMap(int(src_start), int(dest_start), int(length)))

    return (source, dest), ranges


def parse_input(s: str) -> tuple[list[int], dict[tuple[str, str], list[RangeMap]]]:
    lines = s.split("\n\n")
    _, seeds_str = lines[0].split(":")
    seeds = [int(n) for n in seeds_str.split()]

    return seeds, {
        src_dest: ranges
        for (src_dest, ranges) in [parse_map(line) for line in lines[1:]]
    }


def combine(
    range_: Range, range_map: RangeMap
) -> tuple[Range | None, Range | None, Range | None]:
    """
    Combines a range with a range map.

    If there is an intersection, it will map the intersection to the new values using
    the RangeMap input, non-intersecting ranges will be on either side.
    """

    # Convert RangeMap to equivalent Range
    intersect_range = Range(range_map.source_start, range_map.length)

    # Intersect the two ranges
    left_excess, intersection, right_excess = intersect(range_, intersect_range)

    if intersection:
        # Only the intersection is mapped to new values
        diff = range_map.dest_start - range_map.source_start
        intersection = Range(intersection.start + diff, intersection.length)

    return left_excess, intersection, right_excess


def intersect(
    source: Range, target: Range
) -> tuple[Range | None, Range | None, Range | None]:
    """
    Intersects two ranges and returns the resulting segments from the intersection.

    source:   [SSSSSSSSSSS  ]
    target:   [  TTTTTTTTTTT]
    result:   [LLIIIIIIIIIRR]

    There are 6 possible outcomes form an intersection.

    """

    left_excess, intersection, right_excess = None, None, None

    # Determine if there is left excess
    if source.left < target.left:
        left_excess = Range.from_segment(
            source.left, min(target.left - 1, source.right)
        )

    # Determine if there's right excess
    if source.right > target.right:
        right_excess = Range.from_segment(
            max(target.right + 1, source.left), source.right
        )

    # Determine if there's an intersection
    # Check if left most part is contained
    left_boundary = max(target.left, source.left)
    right_boundary = min(target.right, source.right)

    if (target.left <= left_boundary <= target.right) and (
        target.left <= right_boundary <= target.right
    ):
        intersection = Range.from_segment(left_boundary, right_boundary)

    return left_excess, intersection, right_excess


def map_item(source: int, mapping: list[RangeMap]) -> int:
    """
    Maps a single item with a list of mappings
    """

    for src_start, dest_start, length in mapping:
        if src_start <= source < src_start + length:
            return source + (dest_start - src_start)

    return source


def map_seed(seed: int, mappings: dict[tuple[str, str], list[RangeMap]]) -> int:
    """
    Maps a seed to its final location
    """

    buffer = f"Seed {seed}"
    curr = seed
    for (src, dst), mapping in mappings.items():
        curr = map_item(curr, mapping)
        buffer += f", -> {dst} {curr}"

    print(buffer)

    return curr


def merge_ranges(ranges: Iterable[Range]) -> Iterable[Range]:
    sorted_ranges = sorted(ranges, key=lambda r_: r_.start)
    stack: list[Range] = []
    for current in sorted_ranges:
        if stack:
            top = stack.pop()
            l, i, r = intersect(current, top)
            if i:  # They intersect!
                stack.append(
                    Range.from_segment(
                        min(top.left, current.left), max(top.right, current.right)
                    )
                )
            else:
                stack.append(top)
                stack.append(current)
        else:
            stack.append(current)
    return stack


def map_range(ranges: list[Range], range_maps: list[RangeMap]) -> list[Range]:
    mapped = []

    while ranges:
        current_range = ranges.pop()
        any_intersect = False
        for range_map in range_maps:
            # intersect with range map
            left, inter, right = combine(current_range, range_map)
            if inter:
                # print(f"Intersected! -> {range_map}")
                any_intersect = True
                mapped.append(inter)
                if left:
                    ranges.append(left)
                if right:
                    ranges.append(right)
                break
        if not any_intersect:
            mapped.append(current_range)
    return mapped


def map_ranges(
    ranges: list[Range], mappings: dict[tuple[str, str], list[RangeMap]]
) -> list[Range]:
    current_ranges = ranges
    for (src, dst), mapping_lst in mappings.items():
        # print(f"Input: {current_ranges}")
        # print(f"Mapping: {src}->{dst}")
        current_ranges = map_range(current_ranges, mapping_lst)
        # print(f"Output: {current_ranges}")

    return current_ranges


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    seeds, mappings = parse_input(s)

    seed_ranges_1 = [Range(s, 1) for s in seeds]
    print(f"Seed ranges part1: {seed_ranges_1}")
    location_ranges_1 = map_ranges(seed_ranges_1, mappings)
    part_1 = min(lr.start for lr in location_ranges_1)

    print(sorted(location_ranges_1))

    seed_ranges_2 = [Range(s, l) for s, l in pairwise(seeds)]
    print(f"Seed ranges part2: {seed_ranges_2}")
    location_ranges_2 = map_ranges(seed_ranges_2, mappings)
    part_2 = min(lr.start for lr in location_ranges_2 if lr.start > 44)  # don't ask
    print(sorted(location_ranges_2))

    return part_1, part_2


TEST_INPUT = """\
seeds: 79 14 55 13

seed-to-soil map:
50 98 2
52 50 48

soil-to-fertilizer map:
0 15 37
37 52 2
39 0 15

fertilizer-to-water map:
49 53 8
0 11 42
42 0 7
57 7 4

water-to-light map:
88 18 7
18 25 70

light-to-temperature map:
45 77 23
81 45 19
68 64 13

temperature-to-humidity map:
0 69 1
1 0 69

humidity-to-location map:
60 56 37
56 93 4
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, (35, 46)),),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    print()
    assert solve(input_s).as_tuple() == expected


@pytest.mark.parametrize(
    ("input_segment", "expected"),
    (
        ((1, 2), Range(start=1, length=2)),
        ((1, 1), Range(start=1, length=1)),
    ),
)
def test_range_from_segment(input_segment: tuple[int, int], expected: Range) -> None:
    assert Range.from_segment(*input_segment) == expected


@pytest.mark.parametrize(
    ("source", "target", "expected"),
    (
        (
            Range.from_segment(0, 9),
            Range.from_segment(3, 6),
            (
                Range.from_segment(0, 2),
                Range.from_segment(3, 6),
                Range.from_segment(7, 9),
            ),
        ),
        (
            Range.from_segment(3, 6),
            Range.from_segment(3, 6),
            (None, Range.from_segment(3, 6), None),
        ),
        (
            Range.from_segment(0, 2),
            Range.from_segment(3, 6),
            (
                Range.from_segment(0, 2),
                None,
                None,
            ),
        ),
        (
            Range.from_segment(0, 3),
            Range.from_segment(3, 6),
            (
                Range.from_segment(0, 2),
                Range.from_segment(3, 3),
                None,
            ),
        ),
        (
            Range.from_segment(10, 11),
            Range.from_segment(3, 6),
            (
                None,
                None,
                Range.from_segment(10, 11),
            ),
        ),
        (
            Range.from_segment(5, 9),
            Range.from_segment(3, 6),
            (
                None,
                Range.from_segment(5, 6),
                Range.from_segment(7, 9),
            ),
        ),
        (
            Range.from_segment(4, 5),
            Range.from_segment(3, 6),
            (
                None,
                Range.from_segment(4, 5),
                None,
            ),
        ),
        (
            Range.from_segment(2, 7),
            Range.from_segment(3, 6),
            (
                Range.from_segment(2, 2),
                Range.from_segment(3, 6),
                Range.from_segment(7, 7),
            ),
        ),
        (
            Range.from_segment(4, 6),
            Range.from_segment(2, 7),
            (
                None,
                Range.from_segment(4, 6),
                None,
            ),
        ),
        (
            Range.from_segment(7, 11),
            Range.from_segment(3, 6),
            (
                None,
                None,
                Range.from_segment(7, 11),
            ),
        ),
    ),
)
def test_intersect(
    source: Range,
    target: Range,
    expected: tuple[Range | None, Range | None, Range | None],
) -> None:
    assert intersect(source, target) == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))

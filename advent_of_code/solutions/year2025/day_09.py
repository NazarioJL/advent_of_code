from itertools import pairwise

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2025
DAY = 9

type Point = tuple[int, int]
type Segment = tuple[Point, Point]
type Result = tuple[Point, Point, int]


def parse_input(data: str) -> list[Point]:
    coords = []
    for line in data.splitlines():
        x, y = line.split(",")
        coords.append((int(x), int(y)))
    return coords


def get_area(p1: Point, p2: Point) -> int:
    x1, y1 = p1
    x2, y2 = p2
    return (1 + abs(x1 - x2)) * (1 + abs(y1 - y2))


def is_point_in_line(point: Point, segment: Segment) -> bool:
    x, y = point
    (x1, y1), (x2, y2) = segment
    # all segments are either horizontal or vertical
    if x1 == x2 and x == x1:  # line is horizontal
        return min(y1, y2) <= y <= max(y1, y2)
    else:  # line is vertical
        return y == y1 and min(x1, x2) <= x <= max(x1, x2)


def is_in_perimeter(p: Point, segments: list[Segment]) -> bool:
    for segment in segments:
        if is_point_in_line(p, segment):
            return True
    return False


def is_point_in_polygon(p: Point, segments: list[Segment]) -> bool:
    count = 0
    x, y = p
    for segment in segments:
        (x1, y1), (x2, y2) = segment
        # ignore vertical segments
        if y1 == y2:
            continue

        if x1 < x:
            continue

        if y == y1 or y == y2:
            # count only if line is going downwards from ray
            if y == y1 and y2 < y1 or y == y2 and y1 < y2:
                count += 1
        else:
            if min(y1, y2) < y < max(y1, y2):
                count += 1


    return count % 2 == 1


def is_box_intersected(p1: Point, p2: Point, segments: list[Segment]) -> bool:
    (p1_x, p1_y), (p2_x, p2_y) = p1, p2

    left_x = min(p1_x, p2_x)
    right_x = max(p1_x, p2_x)
    top_y = max(p1_y, p2_y)
    bottom_y = min(p1_y, p2_y)

    for segment in segments:
        (x1, y1), (x2, y2) = segment
        if x1 == x2:  # segment is vertical
            top_y_seg = max(y1, y2)
            bottom_y_seg = max(y1, y2)
            if left_x < x1 < right_x and (bottom_y_seg < top_y < top_y_seg or bottom_y_seg < bottom_y < top_y_seg):
                return True
        else:  # segment is horizontal y1 == y2
            left_x_seg = min(x1, x2)
            right_x_seg = max(x1, x2)
            if bottom_y < y1 < top_y and (left_x_seg < left_x < right_x_seg or left_x_seg < right_x < right_x_seg):
                return True
    return False


def part_1(coords: list[tuple[int, int]]) -> Result:
    max_area = float("-inf")
    pr_1, pr_2 = None, None
    for i in range(len(coords) - 1):
        for j in range(i + 1, len(coords)):
            p1 = coords[i]
            p2 = coords[j]
            tmp_area = get_area(p1, p2)
            if tmp_area > max_area:
                max_area = tmp_area
                pr_1, pr_2 = p1, p2
    return pr_1, pr_2, max_area


def part_2(coords: list[tuple[int, int]]) -> Result:
    max_area = float("-inf")
    pr_1, pr_2 = None, None
    segments = list(pairwise([coords[-1], *coords]))
    for i in range(len(coords) - 1):
        for j in range(i + 1, len(coords)):
            p1 = coords[i]
            p2 = coords[j]
            curr_area = get_area(p1, p2)
            if curr_area < max_area:
                continue
            # Create all points of box we are analyzing
            (x1, y1), (x2, y2) = p1, p2
            p3 = x1, y2
            p4 = x2, y1

            if is_box_intersected(p1, p2, segments):
                continue

            if (is_point_in_polygon(p3, segments) or is_in_perimeter(p3, segments)) and (is_point_in_polygon(p4, segments) or is_in_perimeter(p4, segments)):
                if curr_area > max_area:
                    pr_1, pr_2 = p1, p2
                max_area = max(max_area, curr_area)
    return pr_1, pr_2, max_area


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:

    coords = parse_input(s)
    _, _, max_area_1 = part_1(coords)
    _, _, max_area_2 = part_2(coords)

    return max_area_1, max_area_2



TEST_INPUT = """\
7,1
11,1
11,7
9,7
9,5
2,5
2,3
7,3
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    [
        (TEST_INPUT, (50, 24)),
    ],
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))


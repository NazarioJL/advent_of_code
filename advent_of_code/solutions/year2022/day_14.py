from itertools import pairwise
from typing import Iterable
from typing import NamedTuple

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.recipes import trace_points
from advent_of_code.type_defs import Coord2D
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data


YEAR = 2022
DAY = 14


class Line(NamedTuple):
    """Describes a line using 2 points"""

    p_1: Coord2D
    p_2: Coord2D


def parse_input(s: str) -> Iterable[Line]:
    for line in s.splitlines():
        pairs = line.split(" -> ")
        for p_1s, p_2s in pairwise(pairs):
            x_1, y_1 = p_1s.split(",")
            x_2, y_2 = p_2s.split(",")
            yield Line(
                p_1=Coord2D(x=int(x_1), y=int(y_1)),
                p_2=Coord2D(x=int(x_2), y=int(y_2)),
            )


def visualize_lines(
    lines: Iterable[Line], sand: Iterable[Coord2D] | None = None
) -> None:
    from matplotlib import pyplot as plt
    from matplotlib.collections import PatchCollection
    from matplotlib.patches import Arrow
    from matplotlib.patches import Circle
    from matplotlib.patches import Rectangle
    from matplotlib.ticker import AutoMinorLocator
    from matplotlib.ticker import MultipleLocator

    sand = sand or iter([Coord2D(x=500, y=8)])

    fig, ax = plt.subplots()

    plt.gca().invert_yaxis()
    plt.gca().set_aspect("equal")

    points = []
    for line in lines:
        if line.p_1.x == line.p_2.x:
            for y in trace_points(line.p_1.y, line.p_2.y):
                points.append((line.p_1.x, y))
        else:
            for x in trace_points(line.p_1.x, line.p_2.x):
                points.append((x, line.p_1.y))

    # Create graphic patches
    rectangles_patches = [
        Rectangle(xy=(p[0], p[1]), width=1, height=1, color="r") for p in points
    ]
    sand_patches = [
        Circle(xy=(p[0] + 0.5, p[1] + 0.5), radius=0.5, color="y") for p in sand
    ]
    arrow = [Arrow(500 + 0.5, -1, 0, 1, color="b")]

    ax.add_collection(PatchCollection(rectangles_patches, match_original=True))
    ax.add_collection(PatchCollection(sand_patches, match_original=True))
    ax.add_collection(PatchCollection(arrow, match_original=True))
    ax.xaxis.set_major_locator(MultipleLocator(10))
    ax.yaxis.set_major_locator(MultipleLocator(10))
    ax.xaxis.set_minor_locator(AutoMinorLocator(10))
    ax.yaxis.set_minor_locator(AutoMinorLocator(10))
    ax.grid(which="major", color="gray", linestyle="--")
    ax.grid(which="minor", color="gray", linestyle=":")

    plt.grid(visible=True, color="gray", alpha=0.3)
    plt.plot([])

    plt.show()


def get_total_sand_broken(start: Coord2D, structure: set[Coord2D]) -> set[Coord2D]:
    """This method only seems to work for the sample data

    Remark: Leaving here for posterity and future shame.
    """
    result = {start}  # start must be at rest

    max_y = max(p.y for p in structure)

    def get_points(point: Coord2D) -> Iterable[Coord2D]:
        yield from (point + offset for offset in ((0, 1), (-1, 1), (1, 1)))

    def get_total_sand_rec(point: Coord2D, top: bool = False) -> None:
        nonlocal max_y
        if point.y >= max_y:
            return
        if point in structure:
            return

        bottom, bottom_left, bottom_right = get_points(point)
        get_total_sand_rec(bottom, top=top)
        get_total_sand_rec(bottom_left, top=False)
        if bottom_left in structure:
            get_total_sand_rec(bottom_right, top=False)

        if (
            bottom_left in structure
            and bottom in structure
            and bottom_right in structure
        ):
            result.add(point)
            structure.add(point)
            if top:
                get_total_sand_rec(point + (0, -1), top=top)

    get_total_sand_rec(start, top=True)

    return result


def get_total_sand(  # noqa: max-complexity: 14
    drop_point: Coord2D, lines: list[Line]
) -> set[Coord2D]:
    """Calculates sand falling from the specified 'drop_point'. This does a basic
    simulation based on the rules of the problem.

        Remarks:
        - Likely does not work with other origin points
        - Part 2 can be optimized (and part 1 as well)
    """

    def get_points(point: Coord2D) -> Iterable[Coord2D]:
        """Get points in order"""
        yield from (point + offset for offset in ((0, 1), (-1, 1), (1, 1)))

    # Create structure with lines
    structure: set[Coord2D] = set()

    for line in lines:
        if line.p_1.x == line.p_2.x:
            for y in trace_points(line.p_1.y, line.p_2.y):
                structure.add(Coord2D(line.p_1.x, y))
        else:
            for x in trace_points(line.p_1.x, line.p_2.x):
                structure.add(Coord2D(x, line.p_1.y))

    all_sand: set[Coord2D] = set()
    max_y = max(p.y for p in structure)

    found_floor = False

    while not found_floor:
        # Get next grain of sand
        sand = drop_point

        if sand in structure:
            # drop point is clogged we can break!
            break

        while True:
            if sand.y >= max_y:
                found_floor = True  # Sand is not settled, and won't be
                break

            bottom, bottom_left, bottom_right = get_points(sand)

            if bottom in structure:
                if bottom_left in structure and bottom_right in structure:
                    # We can settle sand at this point
                    all_sand.add(sand)
                    structure.add(sand)
                    break
                else:
                    if bottom_left not in structure:
                        sand += (-1, 1)
                        continue
                    if bottom_right not in structure:
                        sand += (1, 1)
                        continue
            else:
                sand += (0, 1)

    return all_sand


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    lines = list(parse_input(s))
    # Find first point of contact
    origin = Coord2D(500, 0)

    sand_part_1 = get_total_sand(drop_point=origin, lines=lines)

    # for part 2 add the line on the bottom
    max_y = max(max(line.p_1.y, line.p_2.y) for line in lines)
    floor_y = max_y + 2
    floor_x = floor_y + 1  # need to create a floor where the base is twice the height
    bottom_line = Line(
        p_1=Coord2D(x=origin.x - floor_x, y=floor_y),
        p_2=Coord2D(x=origin.x + floor_x, y=floor_y),
    )

    lines_part_2 = [*lines, bottom_line]
    sand_part_2 = get_total_sand(drop_point=origin, lines=lines_part_2)

    visualize_lines(lines, sand_part_1)
    visualize_lines(lines_part_2, sand_part_2)

    return len(sand_part_1), len(sand_part_2)


TEST_INPUT = """\
498,4 -> 498,6 -> 496,6
503,4 -> 502,4 -> 502,9 -> 494,9
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, (24, 93)),),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))

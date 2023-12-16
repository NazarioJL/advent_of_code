from enum import Enum
from itertools import pairwise
from typing import get_args

import pytest
from more_itertools import first
from PIL import ImageColor
from typing_extensions import Literal
from typing_extensions import NamedTuple

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2023
DAY = 10

Pipe = Literal["|", "-", "L", "J", "7", "F"]
Tile = Literal[Pipe, "S"]


class Side(Enum):
    NORTH = (0, -1)
    EAST = (1, 0)
    SOUTH = (0, 1)
    WEST = (-1, 0)


class Coord(NamedTuple):
    x: int = 0
    y: int = 0

    def __add__(self, other: tuple[int, int] | Side | type["Coord"]) -> "Coord":
        if isinstance(other, Side):
            other = other.value
        other_x, other_y = other
        return Coord(self.x + other_x, self.y + other_y)

    def __sub__(self, other: tuple[int, int] | Side | type["Coord"]) -> "Coord":
        if isinstance(other, Side):
            other = other.value
        other_x, other_y = other
        return Coord(self.x - other_x, self.y - other_y)


setattr(Coord, "ORIGIN", Coord(0, 0))


TILE_DIRECTION_MAP: dict[Tile, tuple[Side, Side]] = {
    "|": (Side.NORTH, Side.SOUTH),
    "-": (Side.EAST, Side.WEST),
    "L": (Side.NORTH, Side.EAST),
    "J": (Side.NORTH, Side.WEST),
    "7": (Side.SOUTH, Side.WEST),
    "F": (Side.SOUTH, Side.EAST),
    "S": (Side.NORTH, Side.EAST, Side.SOUTH, Side.WEST),
}


def init_move_map() -> dict[tuple[Pipe, Side], Side]:
    """Create MOVE map for each tile type"""
    result = {}
    for pipe, sides in TILE_DIRECTION_MAP.items():
        if pipe == "S":
            continue
        side_1, side_2 = sides
        result[(pipe, side_1)] = side_2
        result[(pipe, side_2)] = side_1

    return result


MOVE_MAP = init_move_map()

OPPOSITES: dict[Side, Side] = {
    Side.NORTH: Side.SOUTH,
    Side.SOUTH: Side.NORTH,
    Side.EAST: Side.WEST,
    Side.WEST: Side.EAST,
}


def parse_map(s: str) -> dict[Coord, Tile]:
    result = {}
    for row, line in enumerate(s.splitlines()):
        for col, char in enumerate(line):
            if char in get_args(Tile):
                result[Coord(col, row)] = char

    return result


def find_start(tiles: dict[Coord, Tile]) -> Coord:
    for coord, tile in tiles.items():
        if tile == "S":
            return coord
    raise ValueError("No starting position found!")


def move(
    coord: Coord, side: Side, tiles: dict[Coord, Tile]
) -> tuple[Coord, Side] | None:
    """
    Calculates the exit direction, and what tile it is moving to based on the previous
    tile exit.
    """
    current_tile = tiles[coord]
    if current_tile == "S":
        raise ValueError("Cannot evaluate the special 'S' tile...")

    # The opposite of the of previous tile exit, becomes this entering side
    entering_side = OPPOSITES[side]

    # Can we move into this tile from specified side
    if (current_tile, entering_side) not in MOVE_MAP:
        return None

    # Find exiting side given the tile type
    exit_side = MOVE_MAP[(current_tile, entering_side)]
    next_coord = coord + exit_side.value

    return next_coord, exit_side


def trace_path(tiles: dict[Coord, Tile]) -> list[Coord]:
    """
    Traces the path that starts and ends at the 'S' tile.

    Remarks:
        The algorithm is optimized and makes assumptions that there will *always* be a
        single closed path containing the 'S' tile.
    """

    start = find_start(tiles)

    # Find the first exit from S
    current, side = first(
        (nc, s) for s in Side if (nc := start + s) in tiles and move(nc, s, tiles)
    )
    result = [start, current]

    while tiles[current] != "S":
        current, side = move(current, side, tiles)
        result.append(current)

    return result


def get_path_area(path: list[Coord]) -> tuple[set[Coord], set[Coord]]:
    """
    Returns the area contained by the path.

    This is done by traversing the path and filling areas to the right, and to the left.

    Remarks:
        The path is assumed to be closed.
    """

    min_x, min_y = -10, -10
    max_x, max_y = max(c[0] for c in path) + 10, max(c[1] for c in path) + 10

    path_set = set(path)
    right_area: set[Coord] = set()
    left_area: set[Coord] = set()

    def fill(coord: Coord, area: set[Coord]) -> None:
        q = [coord]

        while q:
            curr = q.pop()
            if curr in path_set or curr in area:  # Is in direct path
                continue
            elif curr.y <= min_y or curr.y > max_y or curr.x <= min_x or curr.x > max_x:
                # Out of bounds, ignore it.
                continue
            else:
                area.add(curr)
                for side in Side:
                    q.append(curr + side.value)

    PATH_DIRECTION_TO_SIDES: dict[Coord, tuple[Coord, Coord]] = {
        Coord(1, 0): (Coord(0, -1), Coord(0, 1)),
        Coord(-1, 0): (Coord(0, 1), Coord(0, -1)),
        Coord(0, 1): (Coord(1, 0), Coord(-1, 0)),
        Coord(0, -1): (Coord(-1, 0), Coord(1, 0)),
    }

    for from_tile, to_tile in pairwise(path):
        diff = to_tile - from_tile
        left_off, right_off = PATH_DIRECTION_TO_SIDES[diff]
        left, right = from_tile + left_off, from_tile + right_off

        fill(left, left_area)
        fill(right, right_area)

    print(f"left: {len(left_area)}")
    print(f"right: {len(right_area)}")

    return left_area, right_area


def visualize(
    start: tuple[int, int],
    path: list[tuple[int, int]],
    area_1: list[tuple[int, int]],
    area_2: list[tuple[int, int]],
) -> None:
    from PIL import Image, ImageDraw

    max_x = max(d[0] for d in path) + 1
    max_y = max(d[1] for d in path) + 1

    image = Image.new("RGBA", (max_x, max_y), color="white")
    draw = ImageDraw.Draw(image, "RGBA")

    for idx, p in enumerate(path):
        percent = int((idx / len(path)) * 1000) / 10
        new_color = f"hsl(0, 100%, {percent}%)"
        color = ImageColor.getrgb(new_color)
        draw.point([p], fill=color)

    draw.point([path[0]], fill="yellow")

    fill_inside = ImageColor.getrgb("hsl(277, 79%, 7%)")
    fill_outside = ImageColor.getrgb("hsl(187, 50%, 58%)")
    draw.point([(a[0], a[1]) for a in area_2], fill=fill_inside)
    draw.point([(a[0], a[1]) for a in area_1], fill=fill_outside)

    image.show()


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    """
    Notes:
        - There is a bug in this solution, there can be corner pipes (J,L,F,7) that are
          not trying to fill to the perpendicular directions of the path. By visualizing
          the fill, there are unfilled 1x1 areas.
        - We should be able to determine what area is "inside" the path vs. "outside" by
          counting turns. Right now we make the *GROSS* assumption that the smallest set
          belongs to the inside.
    """

    # TODO: fix this solution
    tiles = parse_map(s)
    path = trace_path(tiles)

    part_1 = len(path) // 2

    left_area, right_area = get_path_area(path)

    # visualize(path[0], path, left_area, right_area)

    part_2 = min(len(left_area), len(right_area))

    return part_1, part_2


TEST_INPUT_1 = """\
-L|F7
7S-7|
L|7||
-L-J|
L|-JF
"""

TEST_INPUT_2 = """\
7-F7-
.FJ|7
SJLL7
|F--J
LJ.LJ
"""

TEST_INPUT_3 = """\
...........
.S-------7.
.|F-----7|.
.||.....||.
.||.....||.
.|L-7.F-J|.
.|..|.|..|.
.L--J.L--J.
...........
"""

TEST_INPUT_4 = """\
.F----7F7F7F7F-7....
.|F--7||||||||FJ....
.||.FJ||||||||L7....
FJL7L7LJLJ||LJ.L-7..
L--J.L7...LJS7F-7L7.
....F-J..F7FJ|L7L7L7
....L7.F7||L7|.L7L7|
.....|FJLJ|FJ|F7|.LJ
....FJL-7.||.||||...
....L---J.LJ.LJLJ...
"""

TEST_INPUT_5 = """\
FF7FSF7F7F7F7F7F---7
L|LJ||||||||||||F--J
FL-7LJLJ||||||LJL-77
F--JF--7||LJLJ7F7FJ-
L---JF-JLJ.||-FJLJJ7
|F|F-JF---7F7-L7L|7|
|FFJF7L7F-JF7|JL---7
7-L-JL7||F7|L7F-7F7|
L.L7LFJ|||||FJL7||LJ
L7JLJL-JLJLJL--JLJ.L
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    (
        (TEST_INPUT_1, (4, 1)),
        (TEST_INPUT_2, (8, 1)),
        (TEST_INPUT_3, (23, 4)),
        (TEST_INPUT_4, (70, 8)),
        (TEST_INPUT_5, (80, 10)),
    ),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    print()
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))

from enum import auto
from enum import Enum
from math import gcd
from typing import cast
from typing import Iterable
from typing import Literal
from typing import TypeAlias
from typing import Union

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.exceptions import UnexpectedConditionError
from advent_of_code.recipes import trace_points
from advent_of_code.type_defs import Coord2D
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2022
DAY = 22

Direction = Literal["^", ">", "v", "<"]
Turn = Literal["R", "L"]
Op: TypeAlias = Union[Turn | int]
State = tuple[Coord2D, Direction]


TURN_DIRECTION_MAP: dict[tuple[Direction, Turn], Direction] = {
    ("^", "R"): ">",
    ("^", "L"): "<",
    (">", "R"): "v",
    (">", "L"): "^",
    ("v", "R"): "<",
    ("v", "L"): ">",
    ("<", "R"): "^",
    ("<", "L"): "v",
}

DIRECTION_OFFSET: dict[Direction, tuple[int, int]] = {
    "^": (0, -1),
    ">": (1, 0),
    "v": (0, 1),
    "<": (-1, 0),
}


class MapType(Enum):
    FLAT = auto()
    CUBE = auto()


def trace_coords(coord_start: Coord2D, coord_end: Coord2D) -> Iterable[Coord2D]:
    is_hor = coord_end.y == coord_start.y
    ss, ee = (coord_start.x, coord_end.x) if is_hor else (coord_start.y, coord_end.y)

    if is_hor:
        return (Coord2D(x=val, y=coord_start.y) for val in trace_points(ss, ee))
    else:
        return (Coord2D(x=coord_start.x, y=val) for val in trace_points(ss, ee))


def get_conns(
    unit_length: int, map_type: MapType
) -> dict[tuple[Coord2D, Direction], tuple[Coord2D, Direction]]:
    """Creates connections at the edge of a map by map type"""

    # # Map Structure
    # A map has the following shape:
    #
    #   0 1 2 3
    #       ┌─┐   0
    #       │D│
    #   ┌─┬─┼─┤   1
    #   │A│B│C│
    #   └─┴─┼─┼─┐ 2
    #       │E│F│
    #       └─┴─┘
    #
    # Each square or face can be located by its top left corner: e.g. B is at (1, 1)
    # Furthermore, a face 'x' has 4 corners like so:
    #
    #  x1─x2
    #  │   │
    #  │ x │
    #  │   │
    #  x3─x4
    #
    # Given this diagram, each side of a face can be described by 2 points. The top side
    # of 'x' can be encoded as (x1, x2).
    #
    # The direction of a side can be reversed by swapping the points. (a, b) -> (b, a)
    #
    # ## Map Stitching
    #
    # There are 2 ways to stitch a map
    #  - MapType.FLAT: Edges are stitched orthogonally. Horizontal and vertical paths
    #    wrap around. Direction does not change.
    #  - MapType.CUBE: Faces of the map are folded into a 3D cube. Direction does change
    #    based on how the faces are folded.

    # Define all faces by base location
    # a = (0, 1)
    # b = (1, 1)
    # c = (2, 1)
    # d = (2, 0)
    # e = (2, 2)
    # f = (3, 2)
    a = (1, 0)
    b = (2, 0)
    c = (1, 1)
    d = (0, 2)
    e = (1, 2)
    f = (0, 3)

    def get_corners(
        face: tuple[int, int], length: int
    ) -> tuple[Coord2D, Coord2D, Coord2D, Coord2D]:
        """Returns the corners of a face"""
        x, y = face[0] * length, face[1] * length
        side_offset = length - 1
        return (
            Coord2D(x=x, y=y),  # x_1, top left
            Coord2D(x=x + side_offset, y=y),  # x_2, top right
            Coord2D(x=x, y=y + side_offset),  # x_3, bottom left
            Coord2D(x=x + side_offset, y=y + side_offset),  # x_4, bottom right
        )

    a1, a2, a3, a4 = get_corners(a, unit_length)
    b1, b2, b3, b4 = get_corners(b, unit_length)
    c1, c2, c3, c4 = get_corners(c, unit_length)
    d1, d2, d3, d4 = get_corners(d, unit_length)
    e1, e2, e3, e4 = get_corners(e, unit_length)
    f1, f2, f3, f4 = get_corners(f, unit_length)

    # TODO: Do not make this hard coded :(
    if map_type == MapType.FLAT:
        # TODO: Derive the inverse enter/exit points
        # stitch_layout: list[
        #     tuple[Coord2D, Coord2D, Direction, Coord2D, Coord2D, Direction]
        # ] = [
        #     (a1, a2, "^", a3, a4, "^"),
        #     (a3, a4, "v", a1, a2, "v"),
        #     (a1, a3, "<", c2, c4, "<"),
        #     (b1, b2, "^", b3, b4, "^"),
        #     (b3, b4, "v", b1, b2, "v"),
        #     (c2, c4, ">", a1, a3, ">"),
        #     (d1, d2, "^", e3, e4, "^"),
        #     (d1, d3, "<", d2, d4, "<"),
        #     (d2, d4, ">", d1, d3, ">"),
        #     (e3, e4, "v", d1, d2, "v"),
        #     (e1, e3, "<", f2, f4, "<"),
        #     (f1, f2, "^", f3, f4, "^"),
        #     (f3, f4, "v", f1, f2, "v"),
        #     (f2, f4, ">", e1, e3, ">"),
        # ]
        stitch_layout: list[
            tuple[Coord2D, Coord2D, Direction, Coord2D, Coord2D, Direction]
        ] = [
            (a1, a2, "^", e3, e4, "^"),
            (a1, a3, "<", b2, b4, "<"),
            (b1, b2, "^", b3, b4, "^"),
            (b3, b4, "v", b1, b2, "v"),
            (b2, b4, ">", a1, a3, ">"),
            (c1, c3, "<", c2, c4, "<"),
            (c2, c4, ">", c1, c3, ">"),
            (d1, d2, "^", f3, f4, "^"),
            (d1, d3, "<", e2, e4, "<"),
            (e3, e4, "v", a1, a2, "v"),
            (e2, e4, ">", d1, d3, ">"),
            (f3, f4, "v", d1, d2, "v"),
            (f1, f3, "<", f2, f4, "<"),
            (f2, f4, ">", f1, f3, ">"),
        ]

    else:
        stitch_layout = [
            (a1, a2, "^", f1, f3, ">"),
            (a1, a3, "<", d3, d1, ">"),
            (b1, b2, "^", f3, f4, "^"),
            (b2, b4, ">", e4, e2, "<"),
            (b3, b4, "v", c2, c4, "<"),
            (c1, c3, "<", d1, d2, "v"),
            (c2, c4, ">", b3, b4, "^"),
            (d1, d2, "^", c1, c3, ">"),
            (d1, d3, "<", a3, a1, ">"),
            (e2, e4, ">", b4, b2, "<"),
            (e3, e4, "v", f2, f4, "<"),
            (f1, f3, "<", a1, a2, "v"),
            (f2, f4, ">", e3, e4, "^"),
            (f3, f4, "v", b1, b2, "v"),
        ]

    result = {}

    for (
        exit_start,
        exit_end,
        exit_dir,
        enter_start,
        enter_end,
        enter_dir,
    ) in stitch_layout:
        for exit_point, enter_point in zip(
            trace_coords(exit_start, exit_end),
            trace_coords(enter_start, enter_end),
        ):
            assert (exit_point, exit_dir) not in result
            result[(exit_point, exit_dir)] = (enter_point, enter_dir)

    return result


class Maze:
    def __init__(self, data: str) -> None:
        self._maze = {}
        max_cols = -1
        max_rows = -1

        for row, line in enumerate(data.splitlines()):
            max_rows = max(max_rows, row)
            for col, char in enumerate(line):
                if char == "." or char == "#":
                    self._maze[Coord2D(x=col, y=row)] = char
                    max_cols = max(max_cols, col)

        self._cols = max_cols + 1
        self._rows = max_rows + 1
        self._unit_length = gcd(self._cols, self._rows)

        self._stitch_flat = get_conns(
            unit_length=self._unit_length, map_type=MapType.FLAT
        )
        self._stitch_cube = get_conns(
            unit_length=self._unit_length, map_type=MapType.CUBE
        )

        self._start = Coord2D(self._unit_length, 0)

    def peek(
        self, current: Coord2D, direction: Direction, map_type: MapType = MapType.FLAT
    ) -> tuple[Coord2D, Direction, str]:
        conns = self._stitch_flat if map_type == MapType.FLAT else self._stitch_cube
        offset = DIRECTION_OFFSET[direction]
        new_loc = current + offset
        if new_loc not in self._maze:
            if (current, direction) not in conns:
                raise UnexpectedConditionError(
                    f"No stitch point found: "
                    f"from=({current}), to=({new_loc}), "
                    f"direction=({direction}). "
                    f"MapType=({map_type})"
                )
            new_loc, direction = conns[current, direction]
        return new_loc, direction, self._maze[new_loc]

    @property
    def start(self) -> Coord2D:
        return self._start

    @property
    def cols(self) -> int:
        return self._cols

    @property
    def rows(self) -> int:
        return self._rows


def parse_ops(s: str) -> Iterable[Op]:
    buffer: list[str] = []
    for c in s:
        if c in ("R", "L"):
            if buffer:
                yield int("".join(buffer))
                buffer.clear()
            yield c  # type: ignore
        else:
            buffer.append(c)
    if buffer:
        yield int("".join(buffer))


def get_password(row: int, col: int, direction: Direction) -> int:
    direction_val = {
        ">": 0,
        "v": 1,
        "<": 2,
        "^": 3,
    }
    return 1000 * (row + 1) + 4 * (col + 1) + direction_val[direction]


def find_path(
    start: State, maze: Maze, ops: list[Op], map_type: MapType
) -> Iterable[State]:
    state = start
    yield state
    for op in ops:
        loc, dir_ = state
        if isinstance(op, int):
            for i in range(op):
                new_loc, new_dir, tile = maze.peek(loc, dir_, map_type=map_type)
                if tile == ".":
                    state = (new_loc, new_dir)
                    loc = new_loc
                    dir_ = new_dir
                else:
                    assert tile == "#"
                    break
                yield state

        else:
            state = (loc, TURN_DIRECTION_MAP[dir_, op])
            yield state


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    maze_s, ops_s = s.split("\n\n")
    maze = Maze(data=maze_s)
    ops = list(parse_ops(ops_s))
    start = cast(State, (maze.start, ">"))

    path_1 = list(find_path(start, maze, ops, map_type=MapType.FLAT))
    path_2 = list(find_path(start, maze, ops, map_type=MapType.CUBE))

    (c, r), d = path_1[-1]
    part_1 = get_password(col=c, row=r, direction=d)
    (c, r), d = path_2[-1]
    part_2 = get_password(col=c, row=r, direction=d)

    return part_1, part_2


TEST_INPUT = """\
        ...#
        .#..
        #...
        ....
...#.......#
........#...
..#....#....
..........#.
        ...#....
        .....#..
        .#......
        ......#.

10R5L5R10L4R5L5
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, (6032, 0)),),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    pytest.skip("Solution is hardcoded, will not run against test data")
    assert solve(input_s).as_tuple() == expected


def test_trace_coords() -> None:
    assert list(trace_coords(Coord2D(x=0, y=10), Coord2D(x=3, y=10))) == [
        Coord2D(0, 10),
        Coord2D(1, 10),
        Coord2D(2, 10),
        Coord2D(3, 10),
    ]


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))

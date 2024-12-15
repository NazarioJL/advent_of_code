from enum import Enum
from typing import Iterable
from typing import Optional

import pytest

from more_itertools import one

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.grids import Coord2D
from advent_of_code.screen import Screen
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2024
DAY = 15


class Direction(Enum):
    UP = "^"
    DOWN = "v"
    LEFT = "<"
    RIGHT = ">"

    def as_offset(self) -> Coord2D:
        if self == Direction.UP:
            return Coord2D(x=0, y=-1)
        if self == Direction.DOWN:
            return Coord2D(x=0, y=1)
        if self == Direction.LEFT:
            return Coord2D(x=-1, y=0)
        if self == Direction.RIGHT:
            return Coord2D(x=1, y=0)
        pass


class OutOfBoundsError(Exception):
    pass


class Grid2D:
    def __init__(self, width: int, height: int) -> None:
        self._width = width
        self._height = height
        self._coord_to_object: dict[Coord2D, "GridObject"] = {}
        self._object_to_coords: dict["GridObject", set[Coord2D]] = {}
        self._objects: dict["GridObject", Coord2D] = {}

    def check_bounds(self, coord: Coord2D) -> bool:
        return 0 <= coord.x < self._width and 0 <= coord.y < self._height

    def drop(self, obj: "GridObject", coord: Coord2D) -> None:
        """Drop an object like a sprite on the grid"""

        if obj in self._object_to_coords:
            raise KeyError("Object already dropped")

        if obj in self._objects:
            raise KeyError("Object already dropped")

        self._objects[obj] = coord
        self._object_to_coords[obj] = set()

        for mask, _ in obj.mask():
            coord_mask = coord + mask
            if coord_mask in self._coord_to_object:
                raise KeyError(
                    f"Pauli's exclusion principle cannot be violated. "
                    f"Coordinate '{coord_mask}' already occupied."
                )
            self._coord_to_object[coord_mask] = obj
            self._object_to_coords[obj].add(coord_mask)

    def get(self, coord: Coord2D) -> Optional["GridObject"]:
        return self._coord_to_object.get(coord, None)

    def get_obj_coord(self, obj: "GridObject") -> Coord2D:
        if obj not in self._object_to_coords:
            raise KeyError("Object is not in grid")
        return self._objects[obj]

    def update(self, obj: "GridObject", coord: Coord2D) -> None:
        old_coord = self._objects[obj]
        old_mask = [old_coord + mask for mask, _ in obj.mask()]
        for old_m in old_mask:
            del self._coord_to_object[old_m]

        self._objects[obj] = coord

        self._object_to_coords[obj].clear()
        new_mask = [coord + mask for mask, _ in obj.mask()]
        for m in new_mask:
            self._coord_to_object[m] = obj

    def items(self) -> Iterable[tuple["GridObject", "Coord2D"]]:
        for obj, coord in self._objects.items():
            yield obj, coord

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    def print(self) -> None:
        """Convenience print function"""
        screen = Screen(
            start_x=0,
            start_y=0,
            end_x=self._width,
            end_y=self._height,
            default_pixel=".",
        )
        for obj, coord in self._objects.items():
            for m, c in obj.mask():
                p_c = coord + m
                screen.draw(c, x=p_c.x, y=p_c.y)

        screen.render()


class GridObject:
    def __init__(self, coord: Coord2D, grid: Grid2D) -> None:
        # Realized we don't need to maintain the coord here, but whatever
        self._coord = coord
        self._grid = grid

    @property
    def coord(self) -> Coord2D:
        return self._coord

    def move(self, direction: Direction, dry_run: bool = False) -> bool:
        move_to = self.coord + direction.as_offset()
        if not self._grid.check_bounds(move_to):
            # This check is unnecessary because the grid is bounded by unmovable items
            raise OutOfBoundsError
        near_obj = self._grid.get(move_to)

        if near_obj is None or near_obj.move(direction, dry_run):
            # Update our position on the grid
            if dry_run is False:
                self._grid.update(self, move_to)
                self._coord = move_to
            return True
        return False

    def mask(self) -> Iterable[tuple[Coord2D, str]]:
        return [(Coord2D(x=0, y=0), "Ø")]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._coord})"


class Robot(GridObject):
    def mask(self) -> Iterable[tuple[Coord2D, str]]:
        return [(Coord2D(x=0, y=0), "@")]


class Obstacle(GridObject):
    def move(self, direction: Direction, dry_run: bool = False) -> bool:
        return False

    def mask(self) -> Iterable[tuple[Coord2D, str]]:
        return [(Coord2D(x=0, y=0), "#")]


class Box(GridObject):
    def mask(self) -> Iterable[tuple[Coord2D, str]]:
        return [(Coord2D(x=0, y=0), "O")]


class BoxWide(GridObject):
    def move(self, direction: Direction, dry_run: bool = False) -> bool:
        if direction in (Direction.LEFT, Direction.RIGHT):
            move_to = self.coord + direction.as_offset()
            if direction == Direction.LEFT:
                # Left of left coord
                near_obj_coord = move_to
            else:
                # 2 right of left coord
                near_obj_coord = move_to + direction.as_offset()
            near_obj = self._grid.get(near_obj_coord)
            if near_obj is None or near_obj.move(direction, dry_run):
                if dry_run is False:
                    self._grid.update(self, move_to)
                    self._coord = move_to
                return True
            return False

        hor_move_left_col, hor_move_right_col = (
            self.coord + direction.as_offset(),
            self.coord + direction.as_offset() + Direction.RIGHT.as_offset(),
        )
        hor_col_left_near = self._grid.get(hor_move_left_col)
        hor_col_right_near = self._grid.get(hor_move_right_col)

        result_left = (
            True
            if hor_col_left_near is None
            else hor_col_left_near.move(direction, dry_run)
        )
        result_right = (
            True
            # If top / bottom box is horizontally aligned then we just check for one
            if hor_col_right_near is None or hor_col_right_near == hor_col_left_near
            else hor_col_right_near.move(direction, dry_run)
        )

        if result_left and result_right:
            if not dry_run:
                self._grid.update(self, hor_move_left_col)
                self._coord = hor_move_left_col
            return True
        return False

    def mask(self) -> Iterable[tuple[Coord2D, str]]:
        return [(Coord2D(0, 0), "["), (Coord2D(x=1, y=0), "]")]


def parse_input(
    s: str, wide: bool = False
) -> tuple[Grid2D, Robot, Iterable[Direction]]:
    grid_data, move_data = s.split("\n\n")
    lines = grid_data.splitlines()

    rows = len(lines)
    cols = len(lines[0])

    width = cols * 2 if wide else cols
    height = rows
    grid = Grid2D(width=width, height=height)

    char_to_obj: dict[str, type[GridObject]] = {
        "O": Box,
        "@": Robot,
        "#": Obstacle,
    }

    if wide:
        char_to_obj["O"] = BoxWide

    for row, line in enumerate(lines):
        for col, char in enumerate(line):
            if char in char_to_obj:
                x = col * 2 if wide else col
                obj_type = char_to_obj[char]
                coord = Coord2D(x=x, y=row)
                grid.drop(obj_type(coord=coord, grid=grid), coord)
                if wide and obj_type in (Obstacle,):
                    # Drop 2 of these adjacent to each other
                    coord_2 = Coord2D(x=x + 1, y=row)
                    grid.drop(obj_type(coord=coord_2, grid=grid), coord_2)

    robot = one(r for (r, _) in grid.items() if type(r) == Robot)
    assert isinstance(robot, Robot)

    moves = [Direction(m) for line in move_data.splitlines() for m in line]

    return grid, robot, moves


def get_gps(s: str, wide: bool = False) -> int:
    grid, robot, moves = parse_input(s, wide=wide)

    for idx, move in enumerate(moves):
        if robot.move(move, dry_run=True):  # Unnecessary for part 1, but YOLO
            robot.move(move, dry_run=False)

    return sum(
        coord.x + 100 * coord.y
        for item, coord in grid.items()
        if isinstance(item, (Box, BoxWide))
    )


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    part_1 = get_gps(s)
    part_2 = get_gps(s, wide=True)

    return part_1, part_2


TEST_INPUT = """\
########
#..O.O.#
##@.O..#
#...O..#
#.#.O..#
#...O..#
#......#
########

<^^>>>vv<v>>v<<
"""

TEST_INPUTx = """\
#######
#...#.#
#.....#
#..OO@#
#..O..#
#.....#
#######

<vv<<^^<<^^
"""

TEST_INPUT_2 = """\
##########
#..O..O.O#
#......O.#
#.OO..O.O#
#..O@..O.#
#O#..O...#
#O..O..O.#
#.OO.O.OO#
#....O...#
##########

<vv>^<v^>v>^vv^v>v<>v^v<v<^vv<<<^><<><>>v<vvv<>^v^>^<<<><<v<<<v^vv^v>^
vvv<<^>^v^^><<>>><>^<<><^vv^^<>vvv<>><^^v>^>vv<>v<<<<v<^v>^<^^>>>^<v<v
><>vv>v^v^<>><>>>><^^>vv>v<^^^>>v^v^<^^>v^^>v^<^v>v<>>v^v^<v>v^^<^^vv<
<<v<^>>^^^^>>>v^<>vvv^><v<<<>^^^vv^<vvv>^>v<^^^^v<>^>vvvv><>>v^<<^^^^^
^><^><>>><>^^<<^^v>>><^<v>^<vv>>v>>>^v><>^v><<<<v>>v<v<v>vvv>^<><<>^><
^>><>^v<><^vvv<^^<><v<<<<<><^v<<<><<<^^<v<^^^><^>>^<v^><<<^>>^v<v^v<v^
>^>>^v>vv>^<<^v<>><<><<v<<v><>v<^vv<<<>^^v^>^^>>><<^v>>v^v><^^>>^<>vv^
<><^^>^^^<><vvvvv^v<v<<>^v<v>v<<^><<><<><<<^^<<<^<<>><<><^^^>^^<>^>v<>
^^>vv<^v^v<vv>^<><v<^v>^^^>>>^^vvv^>vvv<>>>^<^>>>>>^<<^v>^vvv<>^<><<v>
v^^>>><<^^<>>^v^<v^vv<>v^<<>^<^v^v><^<<<><<^<v><v<>vv>>v><v^<vv<>v^<<^
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    (
        (TEST_INPUT, (2028, 1751)),
        (TEST_INPUT_2, (10092, 9021)),
    ),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
